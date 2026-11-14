
"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  Plus,
  Search,
  Loader2,
  ShieldCheck,
  LogOut,
  Menu,
  X,
  MessagesSquare,
  UserRound,
  Bot,
  Send,
  ExternalLink,
  MoreHorizontal,
  Share2,
  Copy,
  Check,
  Pin,
  PinOff,
  Trash2,
  Link2,
} from "lucide-react";

import { getCurrentUser, logout as logoutUser } from "@/lib/auth";
import { ApiError } from "@/lib/api";

import {
  getConversations,
  createConversation,
  updateConversation,
  deleteConversation,
  createConversationShare,
} from "@/lib/conversations";

import {
  getMessages,
  sendChatMessage,
} from "@/lib/messages";

import { getCitationSource } from "@/lib/documents";

import type {
  Citation,
  CitationSource,
  Conversation,
  Message,
  User,
} from "@/lib/types";

function formatConversationDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function formatMessageTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ChatPage() {
  const router = useRouter();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesContentRef = useRef<HTMLDivElement>(null);

  const shouldAutoScrollRef = useRef(true);

  const scrollToBottom = useCallback(() => {
    const container = messagesContainerRef.current;

    if (!container) return;

    container.scrollTop = container.scrollHeight;
  }, []);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [user, setUser] = useState<User | null>(null);

  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [activeConversationId, setActiveConversationId] =
    useState<string | null>(null);

  const activeConversationIdRef = useRef<string | null>(null);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  const [messages, setMessages] = useState<Message[]>([]);
  const [messageInput, setMessageInput] = useState("");

  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Conversation action menu state.
  const [openConversationMenuId, setOpenConversationMenuId] =
    useState<string | null>(null);

  // Prevent repeated pin/delete requests for the same conversation.
  const [conversationActionId, setConversationActionId] =
    useState<string | null>(null);

  // Private conversation link feedback.
  const [copiedPrivateLinkId, setCopiedPrivateLinkId] =
    useState<string | null>(null);

  // Public sharing state.
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [shareConversationId, setShareConversationId] =
    useState<string | null>(null);
  const [shareLink, setShareLink] = useState("");
  const [creatingShareLink, setCreatingShareLink] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [shareError, setShareError] = useState("");

  const [error, setError] = useState("");

  // Citation preview state.
  const [selectedCitation, setSelectedCitation] =
    useState<Citation | null>(null);

  const [citationSource, setCitationSource] =
    useState<CitationSource | null>(null);

  const [loadingCitation, setLoadingCitation] = useState(false);
  const [citationError, setCitationError] = useState("");

  const citationRequestRef = useRef(0);

  // Load conversations.
  const loadConversations = useCallback(async () => {
    const result = await getConversations(100, 0);

    setConversations(result);

    setActiveConversationId((currentId) => {
      if (
        currentId &&
        result.some((conversation) => conversation.id === currentId)
      ) {
        return currentId;
      }

      return result[0]?.id ?? null;
    });
  }, []);

  // Verify authentication and initialize workspace.
  useEffect(() => {
    let active = true;

    async function initialize() {
      try {
        const currentUser = await getCurrentUser();

        if (!active) return;

        setUser(currentUser);

        const result = await getConversations(100, 0);

        if (!active) return;

        setConversations(result);

        // Select the conversation requested by a private link.
        const requestedConversationId =
          new URLSearchParams(window.location.search).get(
            "conversation",
          );

        const requestedConversation = requestedConversationId
          ? result.find(
              (conversation) =>
                conversation.id === requestedConversationId,
            )
          : null;

        // A private link only selects a conversation belonging
        // to the authenticated user's conversation list.
        setActiveConversationId(
          requestedConversation?.id ?? result[0]?.id ?? null,
        );
      } catch (err) {
        if (!active) return;

        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load your conversations.",
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    initialize();

    return () => {
      active = false;
    };
  }, [router]);

  // Load messages when the selected conversation changes.
  useEffect(() => {
    if (!activeConversationId) {
      setMessages([]);
      setLoadingMessages(false);
      return;
    }

    let active = true;

    async function loadConversationMessages() {
      setLoadingMessages(true);
      setMessages([]);
      setError("");

      citationRequestRef.current += 1;

      setSelectedCitation(null);
      setCitationSource(null);
      setCitationError("");
      setLoadingCitation(false);

      try {
        const result = await getMessages(
          activeConversationId as string,
          100,
          0,
        );

        if (active) {
          setMessages(result);
        }
      } catch (err) {
        if (!active) return;

        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load conversation messages.",
        );
      } finally {
        if (active) {
          setLoadingMessages(false);
        }
      }
    }

    loadConversationMessages();

    return () => {
      active = false;
    };
  }, [activeConversationId, router]);

  // Reset scroll behavior whenever a different conversation is selected.
  useEffect(() => {
    shouldAutoScrollRef.current = true;

    const container = messagesContainerRef.current;

    if (container) {
      container.scrollTop = 0;
    }
  }, [activeConversationId]);

  // Scroll to the latest message after a conversation loads or new messages arrive.
  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container || loadingMessages || !activeConversationId) {
      return;
    }

    if (!shouldAutoScrollRef.current) {
      return;
    }

    const animationFrame = requestAnimationFrame(() => {
      scrollToBottom();
    });

    return () => cancelAnimationFrame(animationFrame);
  }, [
    activeConversationId,
    messages,
    loadingMessages,
    sendingMessage,
    scrollToBottom,
  ]);

  // Follow message-content height changes without overriding a user's manual scroll.
  useEffect(() => {
    const content = messagesContentRef.current;

    if (!content || loadingMessages || !activeConversationId) {
      return;
    }

    let animationFrame = 0;

    const observer = new ResizeObserver(() => {
      if (!shouldAutoScrollRef.current) {
        return;
      }

      cancelAnimationFrame(animationFrame);

      animationFrame = requestAnimationFrame(() => {
        scrollToBottom();
      });
    });

    observer.observe(content);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(animationFrame);
    };
  }, [
    activeConversationId,
    loadingMessages,
    messages.length,
    scrollToBottom,
  ]);

  // Close citation preview.
  function closeCitationPreview() {
    citationRequestRef.current += 1;

    setSelectedCitation(null);
    setCitationSource(null);
    setLoadingCitation(false);
    setCitationError("");
  }

  // Retrieve the source associated with a citation.
  async function handleCitationClick(citation: Citation) {
    const requestId = ++citationRequestRef.current;

    setSelectedCitation(citation);
    setCitationSource(null);
    setCitationError("");
    setLoadingCitation(true);

    try {
      const source = await getCitationSource(
        citation.document_id,
        citation.chunk_id,
      );

      if (requestId !== citationRequestRef.current) return;

      setCitationSource(source);
    } catch (err) {
      if (requestId !== citationRequestRef.current) return;

      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setCitationError(
        err instanceof Error
          ? err.message
          : "Unable to retrieve this citation source.",
      );
    } finally {
      if (requestId === citationRequestRef.current) {
        setLoadingCitation(false);
      }
    }
  }

  // Create a conversation.
  async function handleCreateConversation() {
    setError("");
    setCreatingConversation(true);

    try {
      const conversation = await createConversation({
        title: "New Conversation",
      });

      setConversations((current) => [
        conversation,
        ...current.filter((item) => item.id !== conversation.id),
      ]);

      setActiveConversationId(conversation.id);
      setMessageInput("");
      setMobileMenuOpen(false);

      closeCitationPreview();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to create a new conversation.",
      );
    } finally {
      setCreatingConversation(false);
    }
  }

  // Create a secure public share link.
  async function handleShareConversation(conversationId: string) {
    setOpenConversationMenuId(null);

    // Remember the exact conversation being shared.
    // This is also used by the retry button.
    setShareConversationId(conversationId);

    setShareDialogOpen(true);
    setShareLink("");
    setShareError("");
    setCopySuccess(false);
    setCreatingShareLink(true);

    try {
      const result = await createConversationShare(conversationId);

      setShareLink(result.share_url);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setShareDialogOpen(false);
        router.replace("/login");
        return;
      }

      setShareError(
        err instanceof Error
          ? err.message
          : "Unable to create a share link.",
      );
    } finally {
      setCreatingShareLink(false);
    }
  }

  // Copy the generated public share link.
  async function handleCopyShareLink() {
    if (!shareLink) return;

    try {
      await navigator.clipboard.writeText(shareLink);

      setCopySuccess(true);

      window.setTimeout(() => {
        setCopySuccess(false);
      }, 2000);
    } catch {
      setShareError(
        "Unable to copy the link. Please copy it manually.",
      );
    }
  }

  // Copy a private conversation URL.
  // This does not create a public share or grant access to another user.
  async function handleCopyPrivateConversationLink(
    conversationId: string,
  ) {
    setOpenConversationMenuId(null);

    const privateLink =
      `${window.location.origin}/dashboard/chat?conversation=${encodeURIComponent(conversationId)}`;

    try {
      await navigator.clipboard.writeText(privateLink);

      setCopiedPrivateLinkId(conversationId);

      window.setTimeout(() => {
        setCopiedPrivateLinkId((current) =>
          current === conversationId ? null : current,
        );
      }, 2000);
    } catch {
      setError(
        "Unable to copy the private link. Please check clipboard permissions.",
      );
    }
  }

  // Pin or unpin a conversation.
  async function handleTogglePin(conversation: Conversation) {
    if (conversationActionId) return;

    setOpenConversationMenuId(null);
    setError("");
    setConversationActionId(conversation.id);

    const nextPinnedState = !conversation.is_pinned;

    try {
      const updatedConversation = await updateConversation(
        conversation.id,
        {
          is_pinned: nextPinnedState,
        },
      );

      setConversations((current) => {
        const updated = current.map((item) =>
          item.id === updatedConversation.id
            ? updatedConversation
            : item,
        );

        return [...updated].sort((a, b) => {
          if (a.is_pinned !== b.is_pinned) {
            return a.is_pinned ? -1 : 1;
          }

          return (
            new Date(b.updated_at).getTime() -
            new Date(a.updated_at).getTime()
          );
        });
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to update the conversation's pinned status.",
      );
    } finally {
      setConversationActionId(null);
    }
  }

  // Delete a conversation after confirmation.
  async function handleDeleteConversation(
    conversation: Conversation,
  ) {
    if (conversationActionId) return;

    setOpenConversationMenuId(null);

    // Do not delete the active conversation while its message
    // request is still running.
    if (
      sendingMessage &&
      activeConversationIdRef.current === conversation.id
    ) {
      setError(
        "Please wait for the current response to finish before deleting this conversation.",
      );
      return;
    }

    const confirmed = window.confirm(
      `Delete "${conversation.title}"?\n\nThis conversation and its messages will be permanently deleted.`,
    );

    if (!confirmed) return;

    setError("");
    setConversationActionId(conversation.id);

    let deletionSucceeded = false;

    try {
      await deleteConversation(conversation.id);

      deletionSucceeded = true;

      setConversations((current) =>
        current.filter((item) => item.id !== conversation.id),
      );

      // If the deleted conversation was active, clear the workspace.
      if (activeConversationIdRef.current === conversation.id) {
        setActiveConversationId(null);
        setMessages([]);
        setMessageInput("");

        closeCitationPreview();

        // Create a replacement separately. If this fails,
        // the original deletion must still be treated as successful.
        try {
          const newConversation = await createConversation({
            title: "New Conversation",
          });

          setConversations((current) => [
            newConversation,
            ...current.filter(
              (item) => item.id !== newConversation.id,
            ),
          ]);

          setActiveConversationId(newConversation.id);
        } catch (createErr) {
          if (
            createErr instanceof ApiError &&
            createErr.status === 401
          ) {
            router.replace("/login");
            return;
          }

          setError(
            "Conversation deleted successfully, but a new conversation could not be created. Use New conversation to continue.",
          );
        }
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete this conversation.",
      );

      // Refresh only when deletion itself failed.
      if (!deletionSucceeded) {
        try {
          await loadConversations();
        } catch {
          // Preserve the original deletion error.
        }
      }
    } finally {
      setConversationActionId(null);
    }
  }

  // Send a message and display it immediately using optimistic UI.
  async function handleSendMessage() {
    const content = messageInput.trim();
    const conversationId = activeConversationId;

    if (!content || !conversationId || sendingMessage) return;

    if (content.length > 20000) {
      setError("Your message cannot exceed 20,000 characters.");
      return;
    }

    const temporaryMessageId = `optimistic-${crypto.randomUUID()}`;

    const optimisticMessage: Message = {
      id: temporaryMessageId,
      role: "user",
      content,
      citations: [],
      created_at: new Date().toISOString(),
    };

    setError("");
    setMessageInput("");

    setMessages((current) => [...current, optimisticMessage]);

    setSendingMessage(true);

    try {
      const response = await sendChatMessage(conversationId, {
        content,
      });

      if (activeConversationIdRef.current === conversationId) {
        setMessages((current) => [
          ...current.filter(
            (message) => message.id !== temporaryMessageId,
          ),
          ...response,
        ]);
      }

      try {
        const updatedConversations = await getConversations(100, 0);

        setConversations(updatedConversations);
      } catch {
        // Do not undo a successful chat response if the sidebar refresh fails.
      }

      textareaRef.current?.focus();
    } catch (err) {
      if (activeConversationIdRef.current === conversationId) {
        setMessages((current) =>
          current.filter(
            (message) => message.id !== temporaryMessageId,
          ),
        );

        setMessageInput((current) => current || content);
      }

      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate an AI response. Please try again.",
      );
    } finally {
      setSendingMessage(false);
    }
  }

  // Enter sends; Shift + Enter inserts a new line.
  function handleMessageKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSendMessage();
    }
  }

  // Logout.
  async function handleLogout() {
    setError("");
    setLoggingOut(true);

    try {
      await logoutUser();

      router.replace("/login");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign out. Please try again.",
      );

      setLoggingOut(false);
    }
  }

  const displayName = user?.full_name || user?.email || "";

  const initials = displayName
    .split(/[\s@]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");

  const activeConversation = conversations.find(
    (conversation) => conversation.id === activeConversationId,
  );

  const pinnedConversations = conversations.filter(
    (conversation) => conversation.is_pinned,
  );

  const recentConversations = conversations.filter(
    (conversation) => !conversation.is_pinned,
  );

  // Render one conversation row and its action menu.
  // The same component is used for pinned and recent conversations.
  function renderConversationItem(
    conversation: Conversation,
    isPinned: boolean,
  ) {
    const isActive = activeConversationId === conversation.id;

    const isMenuOpen =
      openConversationMenuId === conversation.id;

    const isActionRunning =
      conversationActionId === conversation.id;

    return (
      <div
        key={conversation.id}
        className={`group relative flex items-center gap-1 rounded-lg transition ${
          isActive
            ? "bg-primary-light text-primary"
            : "text-foreground hover:bg-secondary"
        }`}
      >
        <button
          type="button"
          onClick={() => {
            setActiveConversationId(conversation.id);
            setMobileMenuOpen(false);
            setMessageInput("");
            setError("");
            setOpenConversationMenuId(null);
          }}
          className="min-w-0 flex-1 rounded-lg px-2.5 py-2.5 text-left"
        >
          <div className="flex items-start gap-3">
            <MessageSquare
              size={17}
              className="mt-0.5 shrink-0"
            />

            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-medium">
                {conversation.title}
              </p>

              <p className="mt-0.5 text-[11px] text-muted">
                {formatConversationDate(conversation.updated_at)}
              </p>
            </div>
          </div>
        </button>

        <button
          type="button"
          aria-label={`Actions for ${conversation.title}`}
          aria-expanded={isMenuOpen}
          onClick={() => {
            setOpenConversationMenuId(
              isMenuOpen ? null : conversation.id,
            );
          }}
          className={`mr-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md transition hover:bg-white hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
            isMenuOpen
              ? "bg-white text-primary"
              : "text-muted opacity-100 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100"
          }`}
        >
          <MoreHorizontal size={18} />
        </button>

        {isMenuOpen && (
          <div className="absolute right-1 top-full z-30 mt-1 w-52 rounded-xl border border-border bg-white p-1.5 shadow-xl">
            <button
              type="button"
              onClick={() =>
                void handleShareConversation(conversation.id)
              }
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-foreground transition hover:bg-primary-light hover:text-primary"
            >
              <Share2 size={16} />
              Share chat
            </button>

            <button
              type="button"
              onClick={() =>
                void handleCopyPrivateConversationLink(
                  conversation.id,
                )
              }
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-foreground transition hover:bg-primary-light hover:text-primary"
            >
              {copiedPrivateLinkId === conversation.id ? (
                <Check size={16} />
              ) : (
                <Link2 size={16} />
              )}

              {copiedPrivateLinkId === conversation.id
                ? "Link copied"
                : "Copy private link"}
            </button>

            <button
              type="button"
              onClick={() =>
                void handleTogglePin(conversation)
              }
              disabled={Boolean(conversationActionId)}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-foreground transition hover:bg-primary-light hover:text-primary disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isActionRunning ? (
                <Loader2 size={16} className="animate-spin" />
              ) : isPinned ? (
                <PinOff size={16} />
              ) : (
                <Pin size={16} />
              )}

              {isActionRunning
                ? isPinned
                  ? "Unpinning..."
                  : "Pinning..."
                : isPinned
                  ? "Unpin chat"
                  : "Pin chat"}
            </button>

            <div className="my-1 border-t border-border" />

            <button
              type="button"
              onClick={() =>
                void handleDeleteConversation(conversation)
              }
              disabled={Boolean(conversationActionId)}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isActionRunning ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Trash2 size={16} />
              )}

              {isActionRunning ? "Deleting..." : "Delete chat"}
            </button>
          </div>
        )}
      </div>
    );
  }

  // Initial loading.
  if (loading) {
    return (
      <main className="flex h-dvh items-center justify-center overflow-hidden bg-secondary">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />

          <p className="text-sm text-muted">
            Loading your AI workspace...
          </p>
        </div>
      </main>
    );
  }

  // Authentication fallback.
  if (!user) {
    return (
      <main className="flex h-dvh items-center justify-center overflow-hidden bg-secondary p-6">
        <div className="max-w-md text-center">
          <h1 className="text-xl font-semibold">
            Unable to load AI Chat
          </h1>

          <p className="mt-3 text-sm text-muted">
            {error || "Your session could not be verified."}
          </p>

          <button
            onClick={() => router.replace("/login")}
            className="mt-6 rounded-xl bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary-dark"
          >
            Return to login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="flex h-dvh overflow-hidden bg-[#f8f7fc]">
      {/* Mobile sidebar overlay */}
      {mobileMenuOpen && (
        <button
          aria-label="Close conversation sidebar"
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
        />
      )}

      {/* Conversation sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-dvh w-64 flex-col border-r border-border bg-white transition-transform lg:static lg:translate-x-0 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-border px-5">
          <Link
            href="/"
            className="text-xl font-bold tracking-tight text-primary"
          >
            Knowly<span className="text-foreground">.</span>
          </Link>

          <button
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close sidebar"
            className="rounded-lg p-2 text-muted hover:bg-secondary lg:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Workspace navigation */}
        <div className="shrink-0 border-b border-border px-3 py-3">
          <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted">
            Workspace
          </p>

          <nav className="space-y-1">
            <Link
              href="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] text-muted transition hover:bg-secondary hover:text-primary"
            >
              <LayoutDashboard size={17} />
              Dashboard
            </Link>

            <Link
              href="/dashboard/documents"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] text-muted transition hover:bg-secondary hover:text-primary"
            >
              <FileText size={17} />
              Documents
            </Link>

            <Link
              href="/dashboard/chat"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg bg-primary-light px-3 py-2.5 text-[13px] font-semibold text-primary"
            >
              <MessageSquare size={17} />
              AI Chat
            </Link>
          </nav>
        </div>

        {/* Conversation controls */}
        <div className="flex shrink-0 items-center justify-between px-4 pb-2 pt-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted">
            Conversations
          </p>

          <button
            onClick={() =>
              void loadConversations().catch((err) =>
                setError(
                  err.message || "Unable to refresh conversations.",
                ),
              )
            }
            aria-label="Refresh conversations"
            title="Refresh conversations"
            className="rounded-lg p-2 text-muted transition hover:bg-secondary hover:text-primary"
          >
            <Search size={16} />
          </button>
        </div>

        {/* New conversation */}
        <div className="shrink-0 px-3">
          <button
            onClick={() => void handleCreateConversation()}
            disabled={creatingConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-[13px] font-semibold text-white transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
          >
            {creatingConversation ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Plus size={18} />
            )}

            New conversation
          </button>
        </div>

        {/* Scrollable conversation list */}
        <div className="min-h-0 flex-1 overflow-y-auto px-2.5 py-3">
          {conversations.length === 0 ? (
            <div className="px-3 py-8 text-center">
              <MessagesSquare
                size={27}
                className="mx-auto text-muted"
              />

              <p className="mt-3 text-sm font-medium">
                No conversations yet
              </p>

              <p className="mt-1 text-xs leading-5 text-muted">
                Create a conversation to start asking questions about your documents.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Pinned conversations */}
              {pinnedConversations.length > 0 && (
                <div>
                  <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted">
                    Pinned
                  </p>

                  <div className="space-y-2">
                    {pinnedConversations.map((conversation) =>
                      renderConversationItem(conversation, true),
                    )}
                  </div>
                </div>
              )}

              {/* Recent conversations */}
              {recentConversations.length > 0 && (
                <div>
                  <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted">
                    Recent
                  </p>

                  <div className="space-y-2">
                    {recentConversations.map((conversation) =>
                      renderConversationItem(conversation, false),
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* User profile */}
        <div className="shrink-0 border-t border-border p-3">
          <div className="flex items-center gap-3 rounded-lg bg-secondary p-2.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-white">
              {initials}
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold">
                {displayName}
              </p>

              <p className="truncate text-[11px] text-muted">
                {user.email}
              </p>
            </div>
          </div>

          <button
            onClick={() => void handleLogout()}
            disabled={loggingOut}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium text-muted transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
          >
            {loggingOut ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <LogOut size={18} />
            )}

            {loggingOut ? "Signing out..." : "Sign out"}
          </button>
        </div>
      </aside>

      {/* Main chat workspace */}
      <section className="flex h-dvh min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-white px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open conversation sidebar"
              className="rounded-lg p-2 text-muted hover:bg-secondary lg:hidden"
            >
              <Menu size={22} />
            </button>

            <div className="min-w-0">
              <h1 className="text-base font-semibold">
                AI Chat
              </h1>

              <p className="truncate text-[11px] text-muted">
                {activeConversation?.title ||
                  "Your document-grounded AI assistant"}
              </p>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2 rounded-full bg-green-50 px-3 py-2 text-xs font-medium text-green-700">
            <ShieldCheck size={15} />
            <span className="hidden sm:inline">Secure session</span>
          </div>
        </header>

        {/* Error message */}
        {error && (
          <div
            role="alert"
            className="mx-auto mt-3 w-full max-w-4xl shrink-0 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {/* Scrollable messages area */}
        <div
          ref={messagesContainerRef}
          onScroll={() => {
            const container = messagesContainerRef.current;

            if (!container) return;

            const distanceFromBottom =
              container.scrollHeight -
              container.scrollTop -
              container.clientHeight;

            shouldAutoScrollRef.current = distanceFromBottom <= 120;
          }}
          className="flex min-h-0 flex-1 flex-col overflow-x-hidden overflow-y-auto overscroll-contain"
        >
          {!activeConversationId ? (
            <div className="flex flex-1 flex-col items-center justify-center p-6 text-center">
              <MessagesSquare size={38} className="text-primary" />

              <h2 className="mt-6 text-2xl font-bold">
                Welcome to Knowly AI
              </h2>

              <p className="mt-3 max-w-md text-sm text-muted">
                Create a new conversation to begin.
              </p>

              <button
                onClick={() => void handleCreateConversation()}
                disabled={creatingConversation}
                className="mt-7 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white hover:bg-primary-dark disabled:opacity-50"
              >
                New conversation
              </button>
            </div>
          ) : loadingMessages ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-3">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />

              <p className="text-sm text-muted">
                Loading conversation messages...
              </p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-1 flex-col items-center justify-center p-6 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-light text-primary">
                <Bot size={32} />
              </div>

              <h2 className="mt-6 text-2xl font-bold">
                Start your conversation
              </h2>

              <p className="mt-3 max-w-md text-sm leading-6 text-muted">
                Ask Knowly questions about your uploaded documents.
                Your answers will be generated using your document knowledge base.
              </p>

              <div className="mt-8 w-full max-w-lg rounded-xl border border-border bg-white p-4 text-left">
                <div className="flex items-center gap-3">
                  <FileText size={20} className="shrink-0 text-primary" />

                  <div>
                    <p className="text-sm font-semibold">
                      Document-grounded answers
                    </p>

                    <p className="mt-1 text-xs leading-5 text-muted">
                      Knowly retrieves relevant document content and generates answers with source citations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div
              ref={messagesContentRef}
              className="mx-auto min-h-max w-full max-w-4xl shrink-0 space-y-6 px-5 py-8 sm:px-8"
            >
              {messages.map((message) => {
                const isUser = message.role === "user";

                const messageParts = message.content.split(
                  /(\[S\d+\])/g,
                );

                return (
                  <article
                    key={message.id}
                    className={`flex items-start gap-3 ${
                      isUser ? "flex-row-reverse" : "flex-row"
                    }`}
                  >
                    <div
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
                        isUser
                          ? "bg-primary text-white"
                          : "bg-white text-primary shadow-sm"
                      }`}
                    >
                      {isUser ? (
                        <UserRound size={18} />
                      ) : (
                        <Bot size={19} />
                      )}
                    </div>

                    <div
                      className={`min-w-0 max-w-[85%] sm:max-w-[78%] ${
                        isUser ? "text-right" : "text-left"
                      }`}
                    >
                      <div className="mb-1 flex items-center gap-2 text-xs text-muted">
                        <span className="font-semibold">
                          {isUser ? "You" : "Knowly AI"}
                        </span>

                        <span>
                          {formatMessageTime(message.created_at)}
                        </span>
                      </div>

                      <div
                        className={`rounded-2xl px-4 py-3 text-left text-sm leading-7 shadow-sm ${
                          isUser
                            ? "rounded-tr-sm bg-primary text-white"
                            : "rounded-tl-sm border border-border bg-white text-foreground"
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words">
                          {messageParts.map((part, index) => {
                            const citationMatch = part.match(
                              /^\[(S\d+)\]$/,
                            );

                            if (!citationMatch || isUser) {
                              return (
                                <span key={`${message.id}-${index}`}>
                                  {part}
                                </span>
                              );
                            }

                            const sourceId = citationMatch[1];

                            const citation = message.citations?.find(
                              (item) =>
                                item.source_id.toUpperCase() === sourceId,
                            );

                            if (!citation) {
                              return (
                                <span key={`${message.id}-${index}`}>
                                  {part}
                                </span>
                              );
                            }

                            return (
                              <button
                                key={`${message.id}-${index}`}
                                type="button"
                                onClick={() =>
                                  void handleCitationClick(citation)
                                }
                                aria-label={`Open source ${sourceId}: ${citation.filename}`}
                                title={`View source: ${citation.filename}`}
                                className="mx-1 inline-flex h-5 min-w-0 items-center justify-center rounded border border-primary/15 bg-primary-light/70 px-1 py-0 align-middle !text-[9px] !leading-none font-medium text-primary transition hover:border-primary hover:bg-primary hover:text-white focus:outline-none focus:ring-1 focus:ring-primary"
                              >
                                {part}
                              </button>
                            );
                          })}
                        </p>
                      </div>

                      {/* Citation source list */}
                      {!isUser && message.citations?.length > 0 && (
                        <div className="mt-2 flex flex-wrap items-center gap-2">
                          {message.citations.map((citation) => (
                            <button
                              key={`${message.id}-${citation.source_id}`}
                              type="button"
                              onClick={() =>
                                void handleCitationClick(citation)
                              }
                              className="inline-flex max-w-full items-center gap-0.5 rounded border border-border bg-white px-1 py-0 text-[8px] leading-none text-muted transition hover:border-primary hover:bg-primary-light hover:text-primary"
                              title={`View ${citation.filename}`}
                            >
                              <FileText size={8} className="shrink-0" />

                              <span className="text-[8px] font-semibold leading-none">
                                [{citation.source_id}]
                              </span>

                              <span className="max-w-40 truncate text-[8px] font-normal leading-none">
                                {citation.filename}
                              </span>

                              <ExternalLink size={8} className="shrink-0" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </article>
                );
              })}

              {sendingMessage && (
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-primary shadow-sm">
                    <Bot size={19} />
                  </div>

                  <div>
                    <p className="mb-1 text-xs font-semibold text-muted">
                      Knowly AI
                    </p>

                    <div className="flex items-center gap-2 rounded-2xl border border-border bg-white px-4 py-3 text-sm text-muted shadow-sm">
                      <Loader2
                        size={16}
                        className="animate-spin text-primary"
                      />

                      Generating your answer...
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Compact fixed message composer */}
        {activeConversationId && (
          <div className="z-10 shrink-0 border-t border-border bg-white px-4 py-3 sm:px-8">
            <div className="mx-auto max-w-3xl">
              <div className="flex items-end gap-2 rounded-2xl border border-border bg-white p-2 shadow-sm focus-within:border-primary">
                <textarea
                  ref={textareaRef}
                  value={messageInput}
                  onChange={(event) => setMessageInput(event.target.value)}
                  onKeyDown={handleMessageKeyDown}
                  placeholder="Ask Knowly anything about your documents..."
                  rows={1}
                  maxLength={20000}
                  disabled={sendingMessage || loadingMessages}
                  aria-label="Write your message"
                  className="max-h-32 min-h-10 flex-1 resize-y bg-transparent px-2 py-2 text-sm text-foreground outline-none placeholder:text-muted disabled:opacity-50"
                />

                <button
                  onClick={() => void handleSendMessage()}
                  disabled={
                    !messageInput.trim() ||
                    sendingMessage ||
                    loadingMessages
                  }
                  aria-label="Send message"
                  title="Send message"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-white transition hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {sendingMessage ? (
                    <Loader2 size={18} className="animate-spin" />
                  ) : (
                    <Send size={18} />
                  )}
                </button>
              </div>

              <div className="mt-2 flex items-center justify-between gap-3 text-[11px] text-muted">
                <span>
                  Enter to send · Shift + Enter for a new line
                </span>

                <span className="shrink-0">
                  {messageInput.length}/20,000
                </span>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Citation source preview overlay */}
      {selectedCitation && (
        <>
          <button
            type="button"
            aria-label="Close citation preview"
            onClick={closeCitationPreview}
            className="fixed inset-0 z-[60] bg-black/30"
          />

          <aside
            role="dialog"
            aria-modal="true"
            aria-labelledby="citation-preview-title"
            className="fixed inset-y-0 right-0 z-[70] flex w-full max-w-md flex-col border-l border-border bg-white shadow-2xl"
          >
            {/* Preview header */}
            <div className="flex shrink-0 items-start justify-between gap-4 border-b border-border px-5 py-5">
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-primary">
                  <FileText size={18} />

                  <span className="text-xs font-semibold uppercase tracking-wider">
                    Source citation
                  </span>
                </div>

                <h2
                  id="citation-preview-title"
                  className="mt-2 text-base font-semibold text-foreground"
                >
                  [{selectedCitation.source_id}] Source
                </h2>

                <p className="mt-1 break-words text-sm text-muted">
                  {selectedCitation.filename}
                </p>
              </div>

              <button
                type="button"
                onClick={closeCitationPreview}
                aria-label="Close citation preview"
                className="shrink-0 rounded-lg p-2 text-muted transition hover:bg-secondary hover:text-foreground"
              >
                <X size={20} />
              </button>
            </div>

            {/* Preview body */}
            <div className="min-h-0 flex-1 overflow-y-auto p-5">
              {loadingCitation ? (
                <div className="flex h-full flex-col items-center justify-center gap-3">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />

                  <p className="text-sm text-muted">
                    Retrieving source content...
                  </p>
                </div>
              ) : citationError ? (
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 p-4"
                >
                  <p className="text-sm font-semibold text-red-700">
                    Unable to load citation
                  </p>

                  <p className="mt-2 text-sm leading-6 text-red-600">
                    {citationError}
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      void handleCitationClick(selectedCitation)
                    }
                    className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                  >
                    Try again
                  </button>
                </div>
              ) : citationSource ? (
                <div className="space-y-5">
                  <div className="rounded-xl border border-border bg-secondary p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted">
                      Document
                    </p>

                    <p className="mt-2 break-words text-sm font-medium text-foreground">
                      {citationSource.filename}
                    </p>

                    <div className="mt-4 flex items-center justify-between gap-3">
                      <span className="text-xs text-muted">
                        Source ID
                      </span>

                      <span className="rounded-md bg-primary-light px-2 py-1 text-xs font-semibold text-primary">
                        {selectedCitation.source_id}
                      </span>
                    </div>

                    <div className="mt-3 flex items-center justify-between gap-3">
                      <span className="text-xs text-muted">
                        Chunk index
                      </span>

                      <span className="text-sm font-medium text-foreground">
                        {citationSource.chunk_index}
                      </span>
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-foreground">
                        Retrieved source text
                      </h3>

                      <span className="text-xs text-muted">
                        {citationSource.content.length} characters
                      </span>
                    </div>

                    <div className="rounded-xl border border-border bg-white p-4">
                      <p className="whitespace-pre-wrap break-words text-sm leading-7 text-foreground">
                        {citationSource.content}
                      </p>
                    </div>
                  </div>

                  <div className="rounded-lg bg-primary-light/60 p-3">
                    <p className="text-xs leading-5 text-primary">
                      This is the original retrieved document chunk used
                      as a source for the AI-generated answer.
                    </p>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Preview footer */}
            <div className="shrink-0 border-t border-border bg-white p-4">
              <button
                type="button"
                onClick={closeCitationPreview}
                className="w-full rounded-xl border border-border bg-white px-4 py-3 text-sm font-semibold text-foreground transition hover:bg-secondary"
              >
                Close source preview
              </button>
            </div>
          </aside>
        </>
      )}

      {/* Conversation share dialog */}
      {shareDialogOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShareDialogOpen(false);
            }
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="share-dialog-title"
            className="w-full max-w-md rounded-2xl border border-border bg-white p-6 shadow-2xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-light text-primary">
                  <Share2 size={21} />
                </div>

                <div>
                  <h2
                    id="share-dialog-title"
                    className="text-lg font-semibold text-foreground"
                  >
                    Share conversation
                  </h2>

                  <p className="mt-1 text-xs text-muted">
                    Create a read-only public link.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShareDialogOpen(false)}
                aria-label="Close share dialog"
                className="rounded-lg p-2 text-muted transition hover:bg-secondary hover:text-foreground"
              >
                <X size={19} />
              </button>
            </div>

            <div className="mt-6">
              {creatingShareLink ? (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-border bg-secondary/50 py-9">
                  <Loader2
                    size={25}
                    className="animate-spin text-primary"
                  />

                  <p className="text-sm text-muted">
                    Creating secure share link...
                  </p>
                </div>
              ) : shareError ? (
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 p-4"
                >
                  <p className="text-sm leading-6 text-red-700">
                    {shareError}
                  </p>

                  <button
                    type="button"
                    onClick={() => {
                      if (shareConversationId) {
                        void handleShareConversation(
                          shareConversationId,
                        );
                      }
                    }}
                    disabled={!shareConversationId}
                    className="mt-3 text-sm font-semibold text-red-700 underline disabled:opacity-50"
                  >
                    Try again
                  </button>
                </div>
              ) : shareLink ? (
                <>
                  <label
                    htmlFor="conversation-share-link"
                    className="mb-2 block text-xs font-semibold text-muted"
                  >
                    PUBLIC SHARE LINK
                  </label>

                  <input
                    id="conversation-share-link"
                    type="text"
                    readOnly
                    value={shareLink}
                    onFocus={(event) => event.target.select()}
                    className="w-full rounded-xl border border-border bg-secondary/50 px-3 py-3 text-sm text-foreground outline-none focus:border-primary"
                  />

                  <button
                    type="button"
                    onClick={() => void handleCopyShareLink()}
                    className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark"
                  >
                    {copySuccess ? (
                      <>
                        <Check size={17} />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy size={17} />
                        Copy link
                      </>
                    )}
                  </button>

                  <p className="mt-4 text-xs leading-5 text-muted">
                    Anyone with this link can view the shared
                    conversation. They cannot modify it. You can
                    revoke access later.
                  </p>
                </>
              ) : null}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
