import { memo, useState } from "react";
import { Bot, User as UserIcon, ChevronRight, Code2 } from "lucide-react";
import type { ChatTurn } from "@/hooks/useChatStream";
import { cn } from "@/lib/utils";
import InlineChart from "./InlineChart";

interface Props {
  turn: ChatTurn;
  onFollowupClick?: (q: string) => void;
}

function ChatMessage({ turn, onFollowupClick }: Props) {
  const isUser = turn.role === "user";

  return (
    <div className="flex gap-2.5">
      {/* Avatar */}
      <div
        className={cn(
          "w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5",
          isUser
            ? "bg-brand-100 text-brand-700 dark:bg-brand-600/20 dark:text-brand-300"
            : "bg-muted text-foreground"
        )}
      >
        {isUser ? <UserIcon className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
      </div>

      {/* Body */}
      <div className="flex-1 min-w-0 space-y-2">
        <p className="text-[11px] font-medium text-muted-foreground">
          {isUser ? "You" : "Safety AI"}
        </p>

        {turn.error ? (
          <p className="text-sm text-red-600 dark:text-red-400">{turn.error}</p>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
              {turn.content}
              {turn.isStreaming && !turn.content && (
                <span className="inline-flex gap-1 ml-1">
                  <span className="w-1 h-1 rounded-full bg-muted-foreground animate-pulse" />
                  <span className="w-1 h-1 rounded-full bg-muted-foreground animate-pulse [animation-delay:150ms]" />
                  <span className="w-1 h-1 rounded-full bg-muted-foreground animate-pulse [animation-delay:300ms]" />
                </span>
              )}
            </p>

            {turn.chart && <InlineChart chart={turn.chart} />}

            {turn.sql && <SqlExpander sql={turn.sql} />}

            {turn.followups && turn.followups.length > 0 && onFollowupClick && (
              <div className="pt-2 space-y-1.5">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Continue exploring
                </p>
                {turn.followups.slice(0, 3).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => onFollowupClick(q)}
                    className="w-full text-left text-xs px-3 py-2 rounded-md border border-border bg-background hover:border-brand-300 hover:bg-brand-50 dark:hover:bg-brand-600/10 dark:hover:border-brand-600/40 transition text-foreground leading-snug"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {turn.cost != null && (
              <p className="text-[10px] text-muted-foreground tabular-nums">
                ${turn.cost.toFixed(3)}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(ChatMessage);

function SqlExpander({ sql }: { sql: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="pt-1">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground hover:text-foreground transition group"
      >
        <ChevronRight
          className={cn(
            "w-3 h-3 transition-transform",
            open && "rotate-90"
          )}
        />
        <Code2 className="w-3 h-3" />
        {open ? "Hide SQL" : "View SQL"}
      </button>

      {open && (
        <pre className="mt-2 p-3 rounded-md bg-muted/60 border border-border text-[11px] leading-relaxed font-mono text-foreground/80 overflow-x-auto whitespace-pre-wrap">
          {sql.trim()}
        </pre>
      )}
    </div>
  );
}