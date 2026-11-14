
import { apiFetch } from "@/lib/api";
import type {
  Conversation,
  ConversationCreate,
  ConversationUpdate,
  SharedConversationRead,
  ConversationShareCreated,
} from "@/lib/types";

export async function getConversations(
  limit = 20,
  offset = 0,
): Promise<Conversation[]> {
  return apiFetch<Conversation[]>(
    `/api/v1/conversations?limit=${limit}&offset=${offset}`,
  );
}

export async function getConversation(
  conversationId: string,
): Promise<Conversation> {
  return apiFetch<Conversation>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
  );
}

export async function createConversation(
  data: ConversationCreate = {},
): Promise<Conversation> {
  return apiFetch<Conversation>(
    "/api/v1/conversations",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}

export async function updateConversation(
  conversationId: string,
  data: ConversationUpdate,
): Promise<Conversation> {
  return apiFetch<Conversation>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(data),
    },
  );
}

export async function deleteConversation(
  conversationId: string,
): Promise<void> {
  return apiFetch<void>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}`,
    {
      method: "DELETE",
    },
  );
}

/**
 * Fetches a publicly shared, read-only conversation.
 * This endpoint does not require viewer authentication.
 */
export async function getSharedConversation(
  token: string,
): Promise<SharedConversationRead> {
  return apiFetch<SharedConversationRead>(
    `/api/v1/conversations/shares/${encodeURIComponent(token)}`,
  );
}

/**
 * Creates a new public share link for an owned conversation.
 */
export async function createConversationShare(
  conversationId: string,
): Promise<ConversationShareCreated> {
  return apiFetch<ConversationShareCreated>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}/share`,
    {
      method: "POST",
    },
  );
}

/**
 * Revokes all active public share links for an owned conversation.
 */
export async function revokeConversationShare(
  conversationId: string,
): Promise<void> {
  return apiFetch<void>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}/share`,
    {
      method: "DELETE",
    },
  );
}