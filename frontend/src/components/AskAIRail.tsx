import { useCallback, useEffect, useRef, useState } from "react";
import { Send, Sparkles, RotateCcw, X } from "lucide-react";
import { useChatStream } from "@/hooks/useChatStream";
import { useRail } from "@/contexts/RailContext";
import { cn } from "@/lib/utils";
import ChatMessage from "./ChatMessage";
import VoiceMicButton from "./VoiceMicButton";

const STARTER_QUESTIONS = [
  "Top 5 states by severe accidents in 2022",
  "Compare California and Texas severity",
  "Which weather conditions are most dangerous?",
  "Show monthly trend of severe incidents",
];

export default function AskAIRail() {
  const { turns, streaming, send, reset } = useChatStream();
  const { railOpen, openRail, closeRail } = useRail();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLInputElement>(null);

  // Refs hold the live values so handleSend can stay reference-stable across
  // keystrokes — otherwise React.memo on ChatMessage would be defeated by a
  // new onFollowupClick prop on every input change.
  const turnsRef = useRef(turns);
  turnsRef.current = turns;
  const streamingRef = useRef(streaming);
  streamingRef.current = streaming;

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [turns]);

  // Auto-focus input when not streaming (initial load + after answer)
// Auto-focus input when rail is open + not streaming
  useEffect(() => {
    if (railOpen && !streaming && inputRef.current) {
      // Small delay so focus happens after the slide-in completes
      const t = setTimeout(() => inputRef.current?.focus(), 250);
      return () => clearTimeout(t);
    }
  }, [streaming, railOpen]);

  // Cmd+K (Mac) / Ctrl+K (Windows) — focus input from anywhere in the app
// Cmd+K (Mac) / Ctrl+K (Windows) — open rail and focus input
  useEffect(() => {
    function handler(e: KeyboardEvent) {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      const cmdKey = isMac ? e.metaKey : e.ctrlKey;
      if (cmdKey && e.key.toLowerCase() === "k") {
        e.preventDefault();
        openRail();
        // Defer focus until after render (rail may have just opened)
        setTimeout(() => {
          inputRef.current?.focus();
          inputRef.current?.select();
        }, 50);
      }
      // Esc to close rail
      if (e.key === "Escape" && railOpen) {
        closeRail();
      }
    }
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [openRail, closeRail, railOpen]);

  const handleSend = useCallback((question: string) => {
    const trimmed = question.trim();
    if (!trimmed || streamingRef.current) return;

    // Build history from prior turns (cap at last 6)
    const history = turnsRef.current
      .slice(-6)
      .filter((t) => !t.error && t.content)
      .map((t) => ({ role: t.role, content: t.content }));

    send({ question: trimmed, history });
    setInput("");
  }, [send]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    handleSend(input);
  }

  return (
    <aside
          className={cn(
            "shrink-0 border-l border-border bg-card flex flex-col h-screen sticky top-0",
            "transition-[width] duration-300 ease-in-out overflow-hidden",
            railOpen ? "w-[380px]" : "w-0 border-l-0"
          )}
          aria-hidden={!railOpen}
        >
{/* Header */}
      <div className="px-5 py-4 border-b border-border flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-brand-50 dark:bg-brand-600/15 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground leading-none">Ask AI</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">Grounded in live data</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {turns.length > 0 && (
            <button
              onClick={reset}
              title="Clear conversation"
              className="w-7 h-7 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition flex items-center justify-center"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={closeRail}
            title="Close (Esc)"
            className="w-7 h-7 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition flex items-center justify-center"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        {turns.length === 0 ? (
          <div className="space-y-3 pt-2">
            <div>
              <p className="text-sm font-medium text-foreground mb-1">
                What would you like to know?
              </p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Ask about incidents, states, weather, or trends.
                I'll pull the data and explain.
              </p>
            </div>
            <div className="space-y-1.5 pt-1">
              {STARTER_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="w-full text-left text-xs px-3 py-2 rounded-md border border-border bg-background hover:border-brand-300 hover:bg-brand-50 dark:hover:bg-brand-600/10 dark:hover:border-brand-600/40 transition text-foreground leading-snug"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          turns.map((t) => (
            <ChatMessage key={t.id} turn={t} onFollowupClick={handleSend} />
          ))
        )}
      </div>

      {/* Input */}
{/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-border p-3 shrink-0">
        <div className="flex items-center gap-2">
<div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={streaming}
              placeholder={streaming ? "Thinking..." : "Ask or press \u2318K…"}
              className="w-full pl-3 pr-20 py-2.5 rounded-lg border border-border bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-transparent transition disabled:opacity-60"
            />

            {/* Cmd+K badge — visible only when input is empty and idle */}
            {!input && !streaming && (
              <kbd className="absolute right-11 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium font-mono text-muted-foreground bg-muted border border-border rounded pointer-events-none">
                ⌘K
              </kbd>
            )}

            <button
              type="submit"
              disabled={streaming || !input.trim()}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-md bg-brand-600 hover:bg-brand-700 text-white disabled:opacity-40 disabled:cursor-not-allowed transition flex items-center justify-center"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
          <VoiceMicButton
            onTranscribed={(text) => {
              const trimmed = text.trim();
              if (!trimmed) return;
              handleSend(trimmed);   // Send immediately after transcription
            }}
            disabled={streaming}
          />
        </div>
      </form>
    </aside>
  );
}