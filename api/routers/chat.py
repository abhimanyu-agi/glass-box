"""/chat/* — streaming AI responses."""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from api.dependencies import get_current_user
from api.models.chat import ChatRequest
from api.models.user import UserPublic
from api.services import agent_service, voice_service


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Streams the agent's response as Server-Sent Events.

    Event types emitted in order:
      - thinking : one-off, right when the request starts
      - narrative: exec-grade prose from the narrator node
      - sql      : the SQL the agent generated (optional)
      - chart    : chart spec ({ type, records, columns }) — optional
      - followups: suggested next questions — optional
      - cost     : total_cost_usd for the call
      - done     : terminator
    """
    history = [m.model_dump() for m in request.history]

    async def event_generator():
        # Kickoff event
        yield {
            "event": "thinking",
            "data":  json.dumps({"message": "Analyzing your question…"}),
        }

        # Run the (blocking) agent in a worker thread so the event loop
        # stays responsive
        try:
            result = await asyncio.to_thread(
                agent_service.run_agent, request.question, history
            )
        except Exception as exc:
            logger.exception("Agent execution failed")
            yield {
                "event": "error",
                "data":  json.dumps({"message": f"Agent failed: {exc}"}),
            }
            yield {"event": "done", "data": json.dumps({})}
            return

        # Narrative (always present)
        narrative = result.get("narrative") or "I couldn't produce an answer."
        yield {
            "event": "narrative",
            "data":  json.dumps({"content": narrative}),
        }

        # SQL (optional — surfaced for transparency)
        sql_query = result.get("generated_sql")
        if sql_query:
            yield {
                "event": "sql",
                "data":  json.dumps({"query": sql_query}),
            }

        # Chart (optional)
        chart_type = result.get("chart_type")
        df         = result.get("query_result_df")
        records    = agent_service.df_to_records(df)
        if records and chart_type:
            yield {
                "event": "chart",
                "data":  json.dumps({
                    "type":    chart_type,
                    "records": records,
                    "columns": list(records[0].keys()) if records else [],
                }),
            }

        # Follow-up suggestions (optional)
        followups = result.get("suggested_followups") or []
        if followups:
            yield {
                "event": "followups",
                "data":  json.dumps({"questions": followups[:3]}),
            }

        # Cost
        yield {
            "event": "cost",
            "data":  json.dumps({
                "total_cost_usd": float(result.get("total_cost_usd") or 0),
            }),
        }

        # Terminator
        yield {"event": "done", "data": json.dumps({})}

    return EventSourceResponse(event_generator())


# ===========================================================================
# Voice — transcribe (Whisper) and speak (TTS)
# ===========================================================================

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Transcribe a recorded audio blob into text using Whisper.
    Accepts webm/opus (browser default), mp3, wav, m4a.
    """
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected audio/*, got {audio.content_type}",
        )

    blob = await audio.read()
    if len(blob) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio is empty",
        )
    if len(blob) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio exceeds 25 MB",
        )

    try:
        text = await asyncio.to_thread(
            voice_service.transcribe, blob, audio.filename or "audio.webm"
        )
    except Exception as exc:
        logger.exception("Whisper transcription failed")
        raise HTTPException(status_code=502, detail=f"Transcription failed: {exc}")

    return {"text": text}


class SpeakRequest(BaseModel):
    text:  str          = Field(..., min_length=1, max_length=4000)
    voice: str | None   = Field(default="nova")


@router.post("/speak")
async def speak_text(
    body: SpeakRequest,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Convert text to speech (MP3) using OpenAI TTS.
    Returns audio/mpeg bytes the browser can play directly.
    """
    valid_voices = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
    voice = (body.voice or "nova").lower()
    if voice not in valid_voices:
        voice = "nova"

    try:
        audio_bytes = await asyncio.to_thread(
            voice_service.synthesize_speech, body.text, voice
        )
    except Exception as exc:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=502, detail=f"TTS failed: {exc}")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="speech.mp3"'},
    )