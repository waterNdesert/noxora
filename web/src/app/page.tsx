"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApiError, currentUser, logout, type UserSummary } from "@/lib/api";

export default function HomePage() {
  const [user, setUser] = useState<UserSummary | null>(null);
  const [message, setMessage] = useState("Checking your session…");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    currentUser()
      .then((current) => {
        if (active) {
          setUser(current);
          setMessage("");
        }
      })
      .catch((error: unknown) => {
        if (!active) return;
        if (error instanceof ApiError && error.status === 401) {
          setMessage("Sign in to continue.");
        } else {
          setMessage("The Nexora API is unavailable. Try again shortly.");
        }
      });
    return () => {
      active = false;
    };
  }, []);

  async function handleLogout() {
    setBusy(true);
    try {
      await logout();
      setUser(null);
      setMessage("You have been signed out.");
    } catch {
      setMessage("Sign out failed. Please retry.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Nexora</h1>
      {message && <p role="status">{message}</p>}
      {user ? (
        <>
          <p>Signed in as {user.full_name || user.email}</p>
          <button type="button" onClick={handleLogout} disabled={busy}>
            {busy ? "Signing out…" : "Sign out"}
          </button>
        </>
      ) : (
        <Link className="button" href="/login">
          Sign in
        </Link>
      )}
    </main>
  );
}
