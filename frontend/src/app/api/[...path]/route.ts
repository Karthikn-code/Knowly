
const BACKEND_URL = process.env.BACKEND_API_URL;


async function proxyRequest(request: Request): Promise<Response> {
  if (!BACKEND_URL) {
    return Response.json(
      { detail: "Backend proxy is not configured." },
      { status: 500 },
    );
  }

  const incomingUrl = new URL(request.url);
  const targetUrl =
    `${BACKEND_URL.replace(/\/+$/, "")}` +
    `${incomingUrl.pathname}` +
    incomingUrl.search;

  const requestHeaders = new Headers(request.headers);

  // Let the backend receive the original browser cookies and Origin.
  requestHeaders.delete("host");
  requestHeaders.delete("connection");
  requestHeaders.delete("content-length");
  requestHeaders.delete("accept-encoding");

  const method = request.method.toUpperCase();
  const hasBody = !["GET", "HEAD"].includes(method);

  try {
    const backendResponse = await fetch(targetUrl, {
      method,
      headers: requestHeaders,
      body: hasBody ? await request.arrayBuffer() : undefined,
      cache: "no-store",
      redirect: "manual",
    });

    const responseHeaders = new Headers(backendResponse.headers);

    // The proxy streams the response, so remove stale transport headers.
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("content-length");
    responseHeaders.delete("transfer-encoding");

    // Preserve every authentication and OAuth cookie separately.
    responseHeaders.delete("set-cookie");

    for (const cookie of backendResponse.headers.getSetCookie()) {
      responseHeaders.append("set-cookie", cookie);
    }

    const responseBody =
      method === "HEAD" ||
      backendResponse.status === 204 ||
      backendResponse.status === 304
        ? null
        : backendResponse.body;

    return new Response(responseBody, {
      status: backendResponse.status,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      { detail: "Unable to connect to the Knowly backend." },
      { status: 502 },
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PATCH = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const OPTIONS = proxyRequest;
export const HEAD = proxyRequest;
