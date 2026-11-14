
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  profile_picture: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: string;
  original_filename: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  is_pinned: boolean;
}

export type MessageRole = "user" | "assistant";

export interface Citation {
  source_id: string;
  document_id: string;
  chunk_id: string;
  filename: string;
  chunk_index: number;
  source_metadata: Record<string, unknown>;
  similarity: number;
}

export interface CitationSource {
  document_id: string;
  chunk_id: string;
  filename: string;
  chunk_index: number;
  content: string;
  source_metadata: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  citations: Citation[];
  created_at: string;
}

export interface MessageCreate {
  content: string;
}

export interface ConversationCreate {
  title?: string;
}

export interface ConversationUpdate {
  title?: string;
  is_pinned?: boolean;
}

export interface ApiErrorResponse {
  detail?: string | Array<{
    msg?: string;
    loc?: (string | number)[];
  }>;
}
export interface SharedMessageRead {
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface SharedConversationRead {
  title: string;
  messages: SharedMessageRead[];
}

export interface ConversationShareCreated {
  id: string;
  share_url: string;
  created_at: string;
}