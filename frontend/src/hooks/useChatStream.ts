import { useCallback, useRef, useState } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { getToken } from "@/lib/api";

export type ChatRole = "user" | "assistant";

export interface ChartPayload {
  type: string;
  records: Record<string, any>[];
  columns: string[];
}

export interface ChatTurn {
  id: string;
  role: ChatRole;
  content: string;
  sql?: string;
  chart?: ChartPayload;
  followups?: string[];
  cost?: number;
  isStreaming?: boolean;
  error?: string;
}

interface SendOptions {
  question: string;
  history: { role: ChatRole; content: string }[];
}

export function useChatStream() {
  const [turns, setTurns]       = useState<ChatTurn[]>([]);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(async ({ question, history }: SendOptions) => {
    if (streaming) return;

    // Add the user turn immediately
    const userTurn: ChatTurn = {
      id: `u-${Date.now()}`,
      role: "user",
      content: question,
    };

    // Placeholder assistant turn (will be filled progressively)
    const asstId = `a-${Date.now()}`;
    const asstTurn: ChatTurn = {
      id: asstId,
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setTurns((prev) => [...prev, userTurn, asstTurn]);
    setStreaming(true);

    // Abort controller so we can cancel
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    const updateAsst = (patch: Partial<ChatTurn>) =>
      setTurns((prev) =>
        prev.map((t) => (t.id === asstId ? { ...t, ...patch } : t))
      );

    try {
      await fetchEventSource("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type":  "application/json",
          Authorization:   `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ question, history }),
        signal: ctrl.signal,
        openWhenHidden: true,

        onmessage(ev) {
          if (!ev.event) return;

          let payload: any = {};
          try { payload = JSON.parse(ev.data); } catch { /* ignore */ }

          switch (ev.event) {
            case "thinking":
              updateAsst({ content: payload.message || "Analyzing…" });
              break;

            case "narrative":
              updateAsst({ content: payload.content || "" });
              break;

            case "sql":
              updateAsst({ sql: payload.query || "" });
              break;


            case "chart":
              updateAsst({
                chart: {
                  type:    payload.type    || "table",
                  records: payload.records || [],
                  columns: payload.columns || [],
                },
              });
              break;

            case "followups":
              updateAsst({ followups: payload.questions || [] });
              break;

            case "cost":
              updateAsst({ cost: payload.total_cost_usd ?? 0 });
              break;

            case "error":
              updateAsst({
                error: payload.message || "Something went wrong.",
                isStreaming: false,
              });
              break;

            case "done":
              updateAsst({ isStreaming: false });
              break;
          }
        },

        onerror(err) {
          updateAsst({
            error: "Connection lost. Please try again.",
            isStreaming: false,
          });
          throw err;   // stop retry loop
        },

        onclose() {
          updateAsst({ isStreaming: false });
        },
      });
    } catch {
      // Errors already shown via updateAsst
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [streaming]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setStreaming(false);
  }, []);

  const reset = useCallback(() => {
    cancel();
    setTurns([]);
  }, [cancel]);

  return { turns, streaming, send, cancel, reset };
}