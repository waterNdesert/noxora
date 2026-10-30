export interface UserSummary {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
}

interface LoginResponse {
  user: UserSummary;
  csrf_token: string;
}

interface CsrfResponse {
  csrf_token: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

let csrfToken: string | null = null;

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: "same-origin",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
    ) {
      message = body.detail;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<UserSummary> {
  const result = await request<LoginResponse>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  csrfToken = result.csrf_token;
  return result.user;
}

export async function currentUser(): Promise<UserSummary> {
  return request<UserSummary>("/api/users/me");
}

export async function logout(): Promise<void> {
  if (!csrfToken) {
    const csrf = await request<CsrfResponse>("/api/auth/csrf");
    csrfToken = csrf.csrf_token;
  }
  await request<void>("/api/auth/logout", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
  });
  csrfToken = null;
}
