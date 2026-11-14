
import type {
  ApiErrorResponse,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000";

const CSRF_COOKIE_NAME = "__Host-knowly_csrf";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(
    message: string,
    status: number,
    details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function getCsrfToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const cookie = document.cookie
    .split("; ")
    .find((item) =>
      item.startsWith(`${CSRF_COOKIE_NAME}=`),
    );

  if (!cookie) {
    return null;
  }

  return decodeURIComponent(
    cookie.substring(CSRF_COOKIE_NAME.length + 1),
  );
}

function isUnsafeMethod(method: string): boolean {
  return !["GET", "HEAD", "OPTIONS"].includes(
    method.toUpperCase(),
  );
}

async function getErrorMessage(
  response: Response,
): Promise<{
  message: string;
  details: unknown;
}> {
  let data: ApiErrorResponse | null = null;

  try {
    data = await response.json() as ApiErrorResponse;
  } catch {
    return {
      message: response.statusText || "Request failed.",
      details: null,
    };
  }

  const detail = data?.detail;

  if (typeof detail === "string") {
    return {
      message: detail,
      details: data,
    };
  }

  if (Array.isArray(detail)) {
    return {
      message: detail
        .map((item) => item.msg || "Invalid request.")
        .join(", "),
      details: data,
    };
  }

  return {
    message: response.statusText || "Request failed.",
    details: data,
  };
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = (options.method || "GET").toUpperCase();

  const headers = new Headers(options.headers);

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  if (isUnsafeMethod(method)) {
    const csrfToken = getCsrfToken();

    if (csrfToken) {
      headers.set("X-CSRF-Token", csrfToken);
    }
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      method,
      headers,
      credentials: "include",
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Unable to connect to Knowly. Check whether the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    const error = await getErrorMessage(response);

    throw new ApiError(
      error.message,
      response.status,
      error.details,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function apiDownload(
  path: string,
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const error = await getErrorMessage(response);

    throw new ApiError(
      error.message,
      response.status,
      error.details,
    );
  }

  return response.blob();
}
