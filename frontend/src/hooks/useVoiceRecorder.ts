import { useCallback, useEffect, useRef, useState } from "react";

export type RecorderStatus =
  | "idle"
  | "requesting-permission"
  | "recording"
  | "processing"
  | "error";

interface UseVoiceRecorderOptions {
  /** Called when transcription succeeds, with the resulting text. */
  onTranscribed?: (text: string) => void;
  /** Hook receives the recorded blob, returns transcribed text. */
  transcribe: (blob: Blob) => Promise<string>;
}

interface UseVoiceRecorderReturn {
  status: RecorderStatus;
  error: string | null;
  /** Begin recording. Triggers a permission prompt the first time. */
  start: () => Promise<void>;
  /** Stop recording and trigger transcription. */
  stop: () => void;
  /** True if currently recording. */
  isRecording: boolean;
}

export function useVoiceRecorder({
  onTranscribed,
  transcribe,
}: UseVoiceRecorderOptions): UseVoiceRecorderReturn {
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [error, setError]   = useState<string | null>(null);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef   = useRef<Blob[]>([]);
  const streamRef   = useRef<MediaStream | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recorderRef.current && recorderRef.current.state !== "inactive") {
        recorderRef.current.stop();
      }
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const start = useCallback(async () => {
    setError(null);

    // Browser support guard
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError("Your browser doesn't support voice recording.");
      setStatus("error");
      return;
    }

    setStatus("requesting-permission");

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err: any) {
      setError(
        err?.name === "NotAllowedError"
          ? "Microphone access denied. Click the lock icon in the address bar to allow."
          : "Could not access microphone."
      );
      setStatus("error");
      return;
    }

    streamRef.current = stream;
    chunksRef.current = [];

    // Pick a mime type the browser supports — fall back gracefully
    const mimeType =
      MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : MediaRecorder.isTypeSupported("audio/mp4")
            ? "audio/mp4"
            : "";

    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    recorderRef.current = recorder;

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = async () => {
      // Free the mic stream
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;

      const blob = new Blob(chunksRef.current, {
        type: mimeType || "audio/webm",
      });

      // Guard against extremely short clips (likely accidental tap)
      if (blob.size < 1000) {
        setStatus("idle");
        setError("Recording was too short. Please try again.");
        return;
      }

      setStatus("processing");
      try {
        const text = await transcribe(blob);
        if (text && onTranscribed) onTranscribed(text);
        setStatus("idle");
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Transcription failed.");
        setStatus("error");
      }
    };

    recorder.start();
    setStatus("recording");
  }, [transcribe, onTranscribed]);

  const stop = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state === "recording") {
      recorderRef.current.stop();
    }
  }, []);

  return {
    status,
    error,
    start,
    stop,
    isRecording: status === "recording",
  };
}