import { Mic, MicOff, Loader2 } from "lucide-react";
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";
import { transcribeAudio } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Props {
  onTranscribed: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceMicButton({ onTranscribed, disabled }: Props) {
  const { status, error, start, stop, isRecording } = useVoiceRecorder({
    transcribe: transcribeAudio,
    onTranscribed,
  });

  const handleClick = () => {
    if (isRecording) stop();
    else start();
  };

  const isProcessing = status === "processing" || status === "requesting-permission";

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled || isProcessing}
        title={
          isRecording ? "Stop recording" :
          isProcessing ? "Transcribing..." :
          "Voice input"
        }
        className={cn(
          "w-9 h-9 rounded-full flex items-center justify-center transition shrink-0",
          isRecording
            ? "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/40 animate-pulse"
            : isProcessing
              ? "bg-muted text-muted-foreground"
              : "bg-muted hover:bg-brand-50 dark:hover:bg-brand-600/15 text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400",
          (disabled || isProcessing) && "cursor-not-allowed opacity-60"
        )}
      >
        {isProcessing ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : isRecording ? (
          <MicOff className="w-4 h-4" />
        ) : (
          <Mic className="w-4 h-4" />
        )}
      </button>

      {/* Recording indicator pill */}
      {isRecording && (
        <div className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2.5 py-1 rounded-full bg-red-500 text-white text-[11px] font-medium whitespace-nowrap flex items-center gap-1.5 shadow-lg shadow-red-500/40">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          Listening
        </div>
      )}

      {/* Status pill (during transcription) */}
      {status === "processing" && (
        <div className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2.5 py-1 rounded-full bg-foreground text-background text-[11px] font-medium whitespace-nowrap shadow-lg">
          Transcribing…
        </div>
      )}

      {/* Error tooltip */}
      {error && status === "error" && (
        <div className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-md bg-destructive text-destructive-foreground text-xs whitespace-nowrap shadow-lg max-w-[260px] truncate">
          {error}
        </div>
      )}
    </div>
  );
}