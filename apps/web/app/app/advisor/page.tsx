"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { sendMessage, getHistory } from "@/lib/api/advisor";
import { track } from "@/lib/analytics";
import { getProperty } from "@/lib/api/properties";
import type { AdvisorMessageResponse, PropertyResponse } from "@/lib/types";

const SUGGESTED_PROMPTS = [
  "Which suburb suits us best?",
  "Compare Broadbeach Waters and Mermaid Waters for us",
  "What should we look for when inspecting?",
  "What are our family's most important priorities?",
];

export default function AdvisorPage() {
  return (
    <Suspense>
      <AdvisorInner />
    </Suspense>
  );
}

function AdvisorInner() {
  const { getToken } = useAuth();
  const searchParams = useSearchParams();
  const propertyId = searchParams.get("property_id");

  const [messages, setMessages] = useState<AdvisorMessageResponse[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [contextProperty, setContextProperty] = useState<PropertyResponse | null>(null);
  const [inlineError, setInlineError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadHistory() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const history = await getHistory(token);
        if (!cancelled) setMessages(history.messages);
      } catch {
        // No history yet — empty state is fine
      } finally {
        if (!cancelled) setHistoryLoading(false);
      }
    }
    loadHistory();
    return () => { cancelled = true; };
  }, [getToken]);

  useEffect(() => {
    if (!propertyId) return;
    let cancelled = false;
    async function loadContextProperty() {
      try {
        const token = await getToken();
        if (!token || cancelled) return;
        const prop = await getProperty(propertyId!, token);
        if (!cancelled) setContextProperty(prop);
      } catch {
        // Context banner just won't show the address
      }
    }
    loadContextProperty();
    return () => { cancelled = true; };
  }, [propertyId, getToken]);

  useEffect(() => {
    if (messages.length > 0 || sending) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, sending]);

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setInlineError(null);

    const optimistic: AdvisorMessageResponse = {
      id: `optimistic-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);
    setSending(true);

    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const reply = await sendMessage(
        { message: text, property_id: propertyId ?? undefined },
        token
      );
      setMessages((prev) => [...prev, reply]);
      track("advisor_message_sent");
    } catch {
      setInlineError("Something went wrong sending your message. Please try again.");
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Context banner */}
      {propertyId && (
        <div className="shrink-0 px-6 py-2 text-sm border-b bg-[#4A9B8E]/10 border-[#4A9B8E]/20 text-[#1A3C5E]">
          {contextProperty
            ? <>Asking about <span className="font-medium">{contextProperty.address_street}, {contextProperty.address_suburb}</span></>
            : "Discussing a saved property"}
        </div>
      )}

      {/* Message thread */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {historyLoading ? (
          <div className="flex justify-center pt-16">
            <ThinkingDots />
          </div>
        ) : messages.length === 0 && !sending ? (
          <EmptyState onSelectPrompt={(p) => setInput(p)} />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="rounded-xl border-l-[3px] border-[#4A9B8E] bg-white px-4 py-3 shadow-sm">
                  <ThinkingDots />
                </div>
              </div>
            )}

            {inlineError && (
              <div className="flex justify-center">
                <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-2">
                  {inlineError}
                </p>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="shrink-0 border-t bg-background px-4 py-3">
        <div className="flex gap-2 max-w-3xl mx-auto items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your move…"
            rows={1}
            disabled={sending}
            aria-label="Message input"
            className="flex-1 resize-none rounded-xl border bg-muted/40 px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#4A9B8E] min-h-[44px] max-h-[120px] disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            aria-label="Send message"
            className="h-10 w-10 shrink-0 flex items-center justify-center rounded-xl bg-[#1A3C5E] text-white disabled:opacity-40 hover:bg-[#1A3C5E]/90 transition-colors"
          >
            <SendIcon />
          </button>
        </div>
        <p className="text-center text-[10px] text-muted-foreground mt-1.5">
          Shift+Enter for new line · Enter to send
        </p>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: AdvisorMessageResponse }) {
  const time = new Date(message.created_at).toLocaleTimeString("en-AU", {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-xl bg-[#1A3C5E] px-4 py-3 text-sm text-white">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-xl border-l-[3px] border-[#4A9B8E] bg-white px-4 py-3 shadow-sm">
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        <p className="text-[10px] text-muted-foreground mt-1.5">{time}</p>
      </div>
    </div>
  );
}

function ThinkingDots() {
  return (
    <div className="flex gap-1 items-center py-1" aria-label="Thinking">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-[#4A9B8E] animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

function EmptyState({ onSelectPrompt }: { onSelectPrompt: (p: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 text-center px-4">
      <p className="text-muted-foreground text-sm max-w-sm leading-relaxed">
        Ask me anything about your move. I know your family, your preferences, and every property you've reviewed.
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSelectPrompt(prompt)}
            className="px-3 py-1.5 text-xs border border-[#4A9B8E]/40 rounded-full text-[#1A3C5E] hover:bg-[#4A9B8E]/10 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

function SendIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  );
}
