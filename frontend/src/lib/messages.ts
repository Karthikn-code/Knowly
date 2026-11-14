
import { apiFetch } from "@/lib/api";
import type {
  Message,
  MessageCreate,
} from "@/lib/types";

export async function getMessages(
  conversationId: string,
  limit = 50,
  offset = 0,
): Promise<Message[]> {
  return apiFetch<Message[]>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}/messages?limit=${limit}&offset=${offset}`,
  );
}

export async function sendChatMessage(
  conversationId: string,
  data: MessageCreate,
): Promise<Message[]> {
  return apiFetch<Message[]>(
    `/api/v1/conversations/${encodeURIComponent(conversationId)}/chat`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}
