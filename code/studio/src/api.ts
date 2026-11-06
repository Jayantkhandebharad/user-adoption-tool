/** Thin client for the management API. Studio is served from the same origin as the API, so
 * the session cookie travels automatically. */

export type Role = "admin" | "editor" | "publisher" | "viewer";

export interface Member {
  id: string;
  email: string;
  name: string;
  role: Role;
}

export interface SetupStatus {
  needs_setup: boolean;
  token_required: boolean;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method,
    credentials: "same-origin",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response));
  }
  return (response.status === 204 ? undefined : await response.json()) as T;
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const { detail } = await response.json();
    if (typeof detail === "string") return detail;
    // FastAPI validation errors: [{ loc, msg }, ...]
    if (Array.isArray(detail) && detail[0]?.msg) return detail.map((d) => d.msg).join(". ");
  } catch {
    // not JSON
  }
  return `Request failed (${response.status})`;
}

export const api = {
  setupStatus: () => request<SetupStatus>("GET", "/api/setup/status"),
  setup: (body: { email: string; name: string; password: string; setup_token?: string }) =>
    request<Member>("POST", "/api/setup", body),
  login: (body: { email: string; password: string }) =>
    request<Member>("POST", "/api/auth/login", body),
  logout: () => request<void>("POST", "/api/auth/logout"),
  me: () => request<Member>("GET", "/api/auth/me"),
};
