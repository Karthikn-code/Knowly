
import { apiFetch, apiDownload } from "@/lib/api";
import type {
  CitationSource,
  Document,
} from "@/lib/types";

export async function getDocuments(
  limit = 20,
  offset = 0,
): Promise<Document[]> {
  return apiFetch<Document[]>(
    `/api/v1/documents?limit=${limit}&offset=${offset}`,
  );
}

export async function uploadDocument(
  file: File,
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<Document>("/api/v1/documents", {
    method: "POST",
    body: formData,
  });
}

export async function getDocument(
  documentId: string,
): Promise<Document> {
  return apiFetch<Document>(
    `/api/v1/documents/${encodeURIComponent(documentId)}`,
  );
}

export async function getCitationSource(
  documentId: string,
  chunkId: string,
): Promise<CitationSource> {
  return apiFetch<CitationSource>(
    `/api/v1/documents/${encodeURIComponent(documentId)}/chunks/${encodeURIComponent(chunkId)}`,
  );
}

export async function downloadDocument(
  documentId: string,
): Promise<Blob> {
  return apiDownload(
    `/api/v1/documents/${encodeURIComponent(documentId)}/download`,
  );
}

export async function deleteDocument(
  documentId: string,
): Promise<void> {
  return apiFetch<void>(
    `/api/v1/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
    },
  );
}
