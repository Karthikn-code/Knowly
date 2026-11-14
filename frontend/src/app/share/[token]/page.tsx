
"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Bot,
  MessageSquare,
  ShieldCheck,
  UserRound,
  AlertCircle,
  Loader2,
} from "lucide-react";

import { ApiError } from "@/lib/api";
import { getSharedConversation } from "@/lib/conversations";
import type { SharedConversationRead } from "@/lib/types";

function formatMessageDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function SharedConversationContent() {
    const params = useParams<{ token: string }>();
  const token = params.token;

  const [conversation, setConversation] =
    useState<SharedConversationRead | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadSharedConversation() {
      setLoading(true);
      setError("");
      setConversation(null);

      try {
        const result = await getSharedConversation(token);

        if (active) {
          setConversation(result);
        }
      } catch (err) {
        if (!active) return;

        if (
  err instanceof ApiError &&
  (err.status === 404 || err.status === 422)
) {
          setError(
            "This shared conversation is unavailable. The link may be invalid or revoked.",
          );
        } else if (err instanceof ApiError && err.status === 0) {
          setError(
            "Unable to connect to Knowly. Please try again later.",
          );
        } else {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load this conversation.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    if (token) {
      loadSharedConversation();
    }

    return () => {
      active = false;
    };
  }, [token]);

  return (
    <main className="min-h-screen bg-[#faf9fd] text-[#171729]">
      <header className="sticky top-0 z-20 border-b border-[#eae8f2] bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4 sm:px-6">
          <Link
            href="/"
            className="flex items-center gap-2"
            aria-label="Knowly home"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#6c4bea] text-white">
              <MessageSquare size={19} />
            </div>

            <span className="text-xl font-bold tracking-tight">
              Knowly
            </span>
          </Link>

          <div className="flex items-center gap-2 rounded-full border border-[#eae8f2] bg-[#faf9fd] px-3 py-1.5">
            <ShieldCheck
              size={15}
              className="text-[#6c4bea]"
            />
            <span className="text-xs font-medium text-[#77778c]">
              Shared conversation
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-12">
        {loading && (
          <div
            className="flex min-h-[55vh] flex-col items-center justify-center gap-4"
            role="status"
          >
            <Loader2
              size={32}
              className="animate-spin text-[#6c4bea]"
            />
            <p className="text-sm text-[#77778c]">
              Loading shared conversation...
            </p>
          </div>
        )}

        {!loading && error && (
          <div className="flex min-h-[55vh] items-center justify-center">
            <div className="w-full max-w-md rounded-2xl border border-[#eae8f2] bg-white p-8 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[#f1edff]">
                <AlertCircle
                  size={26}
                  className="text-[#6c4bea]"
                />
              </div>

              <h1 className="text-xl font-semibold">
                Conversation unavailable
              </h1>

              <p className="mt-3 text-sm leading-6 text-[#77778c]">
                {error}
              </p>

              <Link
                href="/"
                className="mt-6 inline-flex items-center justify-center rounded-xl bg-[#6c4bea] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#5635d5]"
              >
                Go to Knowly
              </Link>
            </div>
          </div>
        )}

        {!loading && !error && conversation && (
          <>
            <section className="mb-8">
              <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#6c4bea]">
                <ShieldCheck size={15} />
                Read-only shared chat
              </div>

              <h1 className="break-words text-2xl font-bold tracking-tight sm:text-3xl">
                {conversation.title || "Untitled conversation"}
              </h1>

              <p className="mt-2 text-sm text-[#77778c]">
                This conversation was shared through Knowly.
                You can read the messages, but cannot modify them.
              </p>
            </section>

            <section
              aria-label="Shared conversation messages"
              className="space-y-5"
            >
              {conversation.messages.length === 0 ? (
                <div className="rounded-2xl border border-[#eae8f2] bg-white px-6 py-12 text-center">
                  <MessageSquare
                    size={28}
                    className="mx-auto mb-3 text-[#aaa4bd]"
                  />

                  <p className="text-sm text-[#77778c]">
                    This conversation has no messages.
                  </p>
                </div>
              ) : (
                conversation.messages.map((message, index) => {
                  const isUser = message.role === "user";

                  return (
                    <article
                      key={`${message.created_at}-${index}`}
                      className={`flex gap-3 ${
                        isUser
                          ? "flex-row-reverse"
                          : "flex-row"
                      }`}
                    >
                      <div
                        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                          isUser
                            ? "bg-[#eeeaff] text-[#6c4bea]"
                            : "bg-[#6c4bea] text-white"
                        }`}
                      >
                        {isUser ? (
                          <UserRound size={18} />
                        ) : (
                          <Bot size={19} />
                        )}
                      </div>

                      <div
                        className={`min-w-0 max-w-[88%] sm:max-w-[82%] ${
                          isUser ? "items-end" : "items-start"
                        } flex flex-col`}
                      >
                        <div className="mb-1 flex items-center gap-2 px-1">
                          <span className="text-xs font-semibold text-[#55546a]">
                            {isUser ? "You" : "Knowly AI"}
                          </span>

                          <span className="text-[11px] text-[#9997a9]">
                            {formatMessageDate(message.created_at)}
                          </span>
                        </div>

                        <div
                          className={`w-full rounded-2xl px-4 py-3 text-sm leading-7 shadow-sm ${
                            isUser
                              ? "rounded-tr-md bg-[#eeeaff] text-[#292344]"
                              : "rounded-tl-md border border-[#eae8f2] bg-white text-[#29283a]"
                          }`}
                        >
                          <p className="whitespace-pre-wrap break-words">
                            {message.content}
                          </p>
                        </div>
                      </div>
                    </article>
                  );
                })
              )}
            </section>

            <footer className="mt-12 border-t border-[#eae8f2] pt-6 text-center">
              <p className="text-xs text-[#9997a9]">
                Shared securely using Knowly.
              </p>
            </footer>
          </>
        )}
      </div>
    </main>
  );
}

export default function SharedConversationPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-[#faf9fd]">
          <div className="flex flex-col items-center gap-3">
            <Loader2
              size={32}
              className="animate-spin text-[#6c4bea]"
            />
            <p className="text-sm text-[#77778c]">
              Loading shared conversation...
            </p>
          </div>
        </main>
      }
    >
      <SharedConversationContent />
    </Suspense>
  );
}