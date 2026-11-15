
import type {
  ApiErrorResponse,
} from "@/lib/types";

const API_BASE_URL = "";

let csrfTokenCache: string | null = null;
let csrfTokenPromise: Promise<string> | null = null;

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

/**
 * Retrieve the CSRF token from the authenticated backend.
 *
 * The CSRF cookie belongs to the backend domain, so the frontend
 * cannot read it directly using document.cookie.
 *
 * The backend returns the session-bound token through this endpoint.
 */
async function getCsrfToken(): Promise<string> {
  if (csrfTokenCache) {
    return csrfTokenCache;
  }

  if (csrfTokenPromise) {
    return csrfTokenPromise;
  }

  csrfTokenPromise = (async () => {
    let response: Response;

    try {
      response = await fetch(
        `${API_BASE_URL}/api/v1/auth/csrf`,
        {
          method: "GET",
          credentials: "include",
          cache: "no-store",
          headers: {
            Accept: "application/json",
          },
        },
      );
    } catch {
      throw new ApiError(
        "Unable to retrieve the security token. Please check your connection.",
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

    const data: {
      csrf_token?: string;
    } = await response.json();

    if (
      typeof data.csrf_token !== "string" ||
      !data.csrf_token
    ) {
      throw new ApiError(
        "The backend returned an invalid security token.",
        response.status,
      );
    }

    csrfTokenCache = data.csrf_token;

    return csrfTokenCache;
  })();

  try {
    return await csrfTokenPromise;
  } finally {
    csrfTokenPromise = null;
  }
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
    const csrfToken = await getCsrfToken();

    headers.set("X-CSRF-Token", csrfToken);
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

  // Clear the cached CSRF token after successful logout.
  if (path.endsWith("/auth/logout")) {
    csrfTokenCache = null;
    csrfTokenPromise = null;
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
