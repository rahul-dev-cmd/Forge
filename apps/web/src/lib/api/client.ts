const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  message: string;
  meta?: {
    page?: number | null;
    limit?: number | null;
    total?: number | null;
    cursor?: string | null;
  } | null;
}

export class ApiError extends Error {
  code: string;
  details?: Record<string, unknown>;
  status: number;

  constructor(message: string, code: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

function resolveAuthToken(): string | null {
  if (typeof window === "undefined") return null;

  const stored = localStorage.getItem("forge_mock_user");
  if (stored) {
    try {
      const user = JSON.parse(stored) as { username?: string };
      if (user.username) return `mock-token-${user.username}`;
    } catch {
      // fall through
    }
  }
  return "mock-token-rahuldev";
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (!headers.has("Authorization")) {
    const token = resolveAuthToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorData: { error?: ApiErrorDetail; detail?: string } | null = null;
      try {
        errorData = await response.json();
      } catch {
        // Fallback if body is not JSON
      }

      const code = errorData?.error?.code || "request_failed";
      const message =
        errorData?.error?.message ||
        (typeof errorData?.detail === "string" ? errorData.detail : null) ||
        `HTTP error! Status: ${response.status}`;
      const details = errorData?.error?.details || {};

      throw new ApiError(message, code, response.status, details);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error instanceof Error ? error.message : "An unexpected network error occurred",
      "network_error",
      500
    );
  }
}

export const apiClient = {
  get: <T>(path: string, options?: RequestInit) =>
    request<T>(path, { ...options, method: "GET" }),

  post: <T>(path: string, body?: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(path: string, body?: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(path: string, body?: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string, options?: RequestInit) =>
    request<T>(path, { ...options, method: "DELETE" }),
};
