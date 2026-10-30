import { afterEach, describe, expect, it, vi } from "vitest";

import { currentUser, login, logout } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("same-origin API client", () => {
  it("uses the opaque browser session for current-user requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "00000000-0000-0000-0000-000000000001",
          email: "admin@example.com",
          full_name: "Admin",
          role: "admin",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(currentUser()).resolves.toMatchObject({ email: "admin@example.com" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/users/me",
      expect.objectContaining({ credentials: "same-origin", cache: "no-store" }),
    );
  });

  it("sends a CSRF token when logging out", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            user: {
              id: "00000000-0000-0000-0000-000000000001",
              email: "admin@example.com",
              full_name: null,
              role: "admin",
            },
            csrf_token: "csrf-value",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await login("admin@example.com", "a sufficiently long password");
    await logout();

    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/auth/logout",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "X-CSRF-Token": "csrf-value" }),
      }),
    );
  });
});
