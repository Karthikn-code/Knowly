
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Download,
  File,
  FileText,
  FileUp,
  Loader2,
  RefreshCw,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import { getCurrentUser } from "@/lib/auth";
import { ApiError } from "@/lib/api";
import {
  getDocuments,
  uploadDocument,
  downloadDocument,
  deleteDocument,
} from "@/lib/documents";
import type { Document, User } from "@/lib/types";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ACCEPTED_EXTENSIONS = [
  ".pdf",
  ".docx",
  ".txt",
  ".pptx",
  ".xlsx",
];

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function statusStyle(status: string): string {
  switch (status.toLowerCase()) {
    case "ready":
      return "bg-green-50 text-green-700";
    case "processing":
      return "bg-amber-50 text-amber-700";
    case "failed":
      return "bg-red-50 text-red-700";
    default:
      return "bg-gray-100 text-gray-700";
  }
}

export default function DocumentsPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [user, setUser] = useState<User | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadDocuments = useCallback(async () => {
    const result = await getDocuments(100, 0);
    setDocuments(result);
  }, []);

  useEffect(() => {
    let active = true;

    async function initialize() {
      try {
        const currentUser = await getCurrentUser();

        if (!active) return;

        setUser(currentUser);

        const result = await getDocuments(100, 0);

        if (active) {
          setDocuments(result);
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
            : "Unable to load your documents.",
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    initialize();

    return () => {
      active = false;
    };
  }, [router]);

  useEffect(() => {
    const hasProcessing = documents.some(
      (document) => document.status.toLowerCase() === "processing",
    );

    if (!hasProcessing) return;

    const interval = window.setInterval(() => {
      loadDocuments().catch(() => {
        // Keep the existing document list if a refresh fails.
      });
    }, 5000);

    return () => window.clearInterval(interval);
  }, [documents, loadDocuments]);

  function validateFile(file: File): string | null {
    const extension = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      return "Unsupported format. Upload PDF, DOCX, TXT, PPTX or XLSX.";
    }

    if (file.size === 0) {
      return "Empty files cannot be uploaded.";
    }

    if (file.size > MAX_FILE_SIZE) {
      return "File size exceeds the 10 MB limit.";
    }

    if (file.name.length > 255) {
      return "Filename must not exceed 255 characters.";
    }

    return null;
  }

  async function handleUpload(file?: File) {
    if (!file) return;

    setError("");
    setSuccess("");

    const validationError = validateFile(file);

    if (validationError) {
      setError(validationError);
      return;
    }

    setUploading(true);

    try {
      await uploadDocument(file);
      await loadDocuments();

      setSuccess(`${file.name} uploaded successfully. Processing has started.`);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to upload the document.",
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(document: Document) {
    setError("");
    setDownloadingId(document.id);

    try {
      const blob = await downloadDocument(document.id);
      const objectUrl = URL.createObjectURL(blob);

      const anchor = window.document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = document.original_filename;
      window.document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to download the document.",
      );
    } finally {
      setDownloadingId(null);
    }
  }

  async function handleDelete(document: Document) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.original_filename}"? This action cannot be undone.`,
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");
    setDeletingId(document.id);

    try {
      await deleteDocument(document.id);

      setDocuments((current) =>
        current.filter((item) => item.id !== document.id),
      );

      setSuccess(`${document.original_filename} was deleted.`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete the document.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-secondary">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted">
            Loading your document library...
          </p>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-secondary p-6">
        <div className="text-center">
          <p className="text-sm text-muted">
            {error || "Unable to verify your account."}
          </p>
          <button
            onClick={() => router.replace("/login")}
            className="mt-4 rounded-xl bg-primary px-5 py-3 text-sm font-medium text-white"
          >
            Return to login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f8f7fc]">
      <header className="border-b border-border bg-white">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-lg font-semibold text-foreground"
          >
            <ArrowLeft size={19} className="text-primary" />
            <span>Knowly</span>
            <span className="text-muted">/</span>
            <span className="text-primary">Documents</span>
          </Link>

          <div className="hidden text-sm text-muted sm:block">
            {user.full_name || user.email}
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl p-5 sm:p-8">
        <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-medium text-primary">
              Your workspace
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight">
              Document Library
            </h1>
            <p className="mt-2 text-sm text-muted">
              Upload, organize and manage your knowledge documents.
            </p>
          </div>

          <button
            onClick={() => loadDocuments().catch((err) =>
              setError(err.message || "Unable to refresh documents."),
            )}
            disabled={uploading}
            className="flex items-center justify-center gap-2 rounded-xl border border-border bg-white px-4 py-3 text-sm font-medium hover:bg-secondary disabled:opacity-50"
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </div>

        {error && (
          <div
            role="alert"
            className="mb-5 flex items-start justify-between gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
          >
            <span>{error}</span>
            <button onClick={() => setError("")} aria-label="Dismiss error">
              <X size={18} />
            </button>
          </div>
        )}

        {success && (
          <div
            role="status"
            className="mb-5 flex items-start justify-between gap-3 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700"
          >
            <span>{success}</span>
            <button onClick={() => setSuccess("")} aria-label="Dismiss message">
              <X size={18} />
            </button>
          </div>
        )}

        <section className="rounded-2xl border border-border bg-white p-6 shadow-sm sm:p-8">
          <div className="flex flex-col items-center text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-light text-primary">
              <FileUp size={27} />
            </div>

            <h2 className="text-lg font-semibold">
              Upload your documents
            </h2>

            <p className="mt-2 max-w-lg text-sm leading-6 text-muted">
              Select a document to add it to your private AI knowledge library.
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.pptx,.xlsx"
              className="hidden"
              disabled={uploading}
              onChange={(event) => {
                const file = event.target.files?.[0];
                void handleUpload(file);
              }}
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="mt-6 flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-50"
            >
              {uploading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Upload size={18} />
              )}
              {uploading ? "Uploading..." : "Choose a document"}
            </button>

            <p className="mt-4 text-xs text-muted">
              PDF, DOCX, TXT, PPTX and XLSX · Maximum 10 MB
            </p>
          </div>
        </section>

        <section className="mt-8">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">
                Your documents
              </h2>
              <p className="mt-1 text-sm text-muted">
                {documents.length} document{documents.length === 1 ? "" : "s"} in your library
              </p>
            </div>
          </div>

          {documents.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-white px-6 py-16 text-center">
              <FileText size={36} className="mx-auto text-muted" />
              <h3 className="mt-4 font-semibold">
                No documents yet
              </h3>
              <p className="mt-2 text-sm text-muted">
                Upload your first document to start building your knowledge library.
              </p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-2xl border border-border bg-white shadow-sm">
              <div className="hidden grid-cols-[minmax(0,1fr)_110px_110px_160px] gap-4 border-b border-border bg-secondary px-6 py-4 text-xs font-semibold uppercase tracking-wide text-muted md:grid">
                <span>Document</span>
                <span>Size</span>
                <span>Status</span>
                <span className="text-right">Actions</span>
              </div>

              <div className="divide-y divide-border">
                {documents.map((document) => (
                  <div
                    key={document.id}
                    className="flex flex-col gap-4 px-5 py-5 sm:px-6 md:grid md:grid-cols-[minmax(0,1fr)_110px_110px_160px] md:items-center"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-light text-primary">
                        <File size={21} />
                      </div>

                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold">
                          {document.original_filename}
                        </p>
                        <p className="mt-1 text-xs text-muted">
                          {document.file_type.toUpperCase()} · {formatDate(document.created_at)}
                        </p>
                      </div>
                    </div>

                    <div className="text-sm text-muted">
                      <span className="md:hidden">Size: </span>
                      {formatFileSize(document.file_size)}
                    </div>

                    <div>
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-medium capitalize ${statusStyle(document.status)}`}
                      >
                        {document.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 md:justify-end">
                      <button
                        onClick={() => void handleDownload(document)}
                        disabled={downloadingId === document.id}
                        title="Download document"
                        aria-label={`Download ${document.original_filename}`}
                        className="rounded-lg border border-border p-2 text-muted hover:bg-secondary hover:text-primary disabled:opacity-50"
                      >
                        {downloadingId === document.id ? (
                          <Loader2 size={17} className="animate-spin" />
                        ) : (
                          <Download size={17} />
                        )}
                      </button>

                      <button
                        onClick={() => void handleDelete(document)}
                        disabled={deletingId === document.id}
                        title="Delete document"
                        aria-label={`Delete ${document.original_filename}`}
                        className="rounded-lg border border-border p-2 text-muted hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                      >
                        {deletingId === document.id ? (
                          <Loader2 size={17} className="animate-spin" />
                        ) : (
                          <Trash2 size={17} />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
