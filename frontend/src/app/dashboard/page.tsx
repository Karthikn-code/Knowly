
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  LogOut,
  ShieldCheck,
  Loader2,
  Menu,
  X,
  ArrowRight,
} from "lucide-react";

import { getCurrentUser, logout as logoutUser } from "@/lib/auth";
import { ApiError } from "@/lib/api";
import type { User } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let active = true;

    async function verifySession() {
      try {
        const currentUser = await getCurrentUser();

        if (active) {
          setUser(currentUser);
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
            : "Unable to verify your session."
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    verifySession();

    return () => {
      active = false;
    };
  }, [router]);

  async function handleLogout() {
    setLoggingOut(true);
    setError("");

    try {
      await logoutUser();
      router.replace("/login");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }

      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign out. Please try again."
      );

      setLoggingOut(false);
    }
  }

  if (loading) {
    return (
      <main className="flex h-dvh items-center justify-center bg-[#f8f7fc]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted">
            Verifying your Knowly session...
          </p>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex h-dvh items-center justify-center bg-[#f8f7fc] p-6">
        <div className="max-w-md text-center">
          <h1 className="text-xl font-semibold">
            Unable to load your dashboard
          </h1>

          <p className="mt-3 text-sm text-muted">
            {error || "Your session could not be verified."}
          </p>

          <button
            onClick={() => router.replace("/login")}
            className="mt-6 rounded-lg bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary-dark"
          >
            Return to login
          </button>
        </div>
      </main>
    );
  }

  const displayName = user.full_name || user.email;

  const initials = displayName
    .split(/[\s@]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");

  return (
    <main className="flex h-dvh overflow-hidden bg-[#f8f7fc]">
      {/* Mobile sidebar overlay */}
      {mobileMenuOpen && (
        <button
          aria-label="Close navigation menu"
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-dvh w-64 flex-col border-r border-border bg-white transition-transform lg:static lg:translate-x-0 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-border px-5">
          <Link
            href="/"
            className="text-xl font-bold tracking-tight text-primary"
          >
            Knowly<span className="text-foreground">.</span>
          </Link>

          <button
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close sidebar"
            className="rounded-lg p-2 text-muted hover:bg-secondary lg:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Workspace navigation */}
        <div className="shrink-0 border-b border-border px-3 py-3">
          <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted">
            Workspace
          </p>

          <nav className="space-y-1">
            {/* Dashboard */}
            <Link
              href="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg bg-primary-light px-3 py-2.5 text-[13px] font-semibold text-primary"
            >
              <LayoutDashboard size={17} />
              Dashboard
            </Link>

            {/* Documents */}
            <Link
              href="/dashboard/documents"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] text-muted transition hover:bg-secondary hover:text-primary"
            >
              <FileText size={17} />
              Documents
            </Link>

            {/* AI Chat */}
            <Link
              href="/dashboard/chat"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] text-muted transition hover:bg-secondary hover:text-primary"
            >
              <MessageSquare size={17} />
              AI Chat
            </Link>
          </nav>
        </div>

        {/* Flexible sidebar space */}
        <div className="min-h-0 flex-1" />

        {/* User profile and logout */}
        <div className="shrink-0 border-t border-border p-3">
          <div className="flex items-center gap-3 rounded-lg bg-secondary p-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white">
              {initials}
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold">
                {displayName}
              </p>

              <p className="truncate text-xs text-muted">
                {user.email}
              </p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium text-muted transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
          >
            {loggingOut ? (
              <Loader2 size={17} className="animate-spin" />
            ) : (
              <LogOut size={17} />
            )}

            {loggingOut ? "Signing out..." : "Sign out"}
          </button>
        </div>
      </aside>

      {/* Main Dashboard */}
      <section className="flex min-h-0 min-w-0 flex-1 flex-col">
        {/* Header - same dimensions as AI Chat */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-white px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
              className="rounded-lg p-2 text-muted hover:bg-secondary lg:hidden"
            >
              <Menu size={20} />
            </button>

            <div className="min-w-0">
              <h1 className="text-base font-semibold">
                Dashboard
              </h1>

              <p className="truncate text-[11px] text-muted">
                Your personal AI workspace
              </p>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2 rounded-full bg-green-50 px-3 py-2 text-xs font-medium text-green-700">
            <ShieldCheck size={15} />
            <span className="hidden sm:inline">
              Secure session
            </span>
          </div>
        </header>

        {/* Scrollable Dashboard Content */}
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl p-5 sm:p-8">
            {error && (
              <div
                role="alert"
                className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
              >
                {error}
              </div>
            )}

            {/* Welcome */}
            <div className="mb-8">
              <p className="text-sm font-medium text-primary">
                Welcome to Knowly
              </p>

              <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground">
                Hello, {user.full_name?.split(" ")[0] || "there"}.
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
                Your AI-powered document workspace is ready.
                Upload your documents and ask questions to
                discover useful information.
              </p>
            </div>

            {/* Workspace Cards */}
            <div className="grid gap-5 md:grid-cols-2">
              {/* Documents Card */}
              <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
                <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-light text-primary">
                  <FileText size={23} />
                </div>

                <h3 className="text-lg font-semibold">
                  Your documents
                </h3>

                <p className="mt-2 text-sm leading-6 text-muted">
                  Upload PDFs and supported documents to build
                  your personal knowledge library.
                </p>

                <Link
                  href="/dashboard/documents"
                  className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-3 text-[13px] font-semibold text-white transition hover:bg-primary-dark"
                >
                  Open Document Library
                  <ArrowRight size={16} />
                </Link>
              </div>

              {/* AI Chat Card */}
              <div className="rounded-2xl border border-border bg-white p-6 shadow-sm">
                <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-light text-primary">
                  <MessageSquare size={23} />
                </div>

                <h3 className="text-lg font-semibold">
                  AI conversations
                </h3>

                <p className="mt-2 text-sm leading-6 text-muted">
                  Ask questions about your uploaded documents
                  and receive AI-generated answers with citations.
                </p>

                <Link
                  href="/dashboard/chat"
                  className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-3 text-[13px] font-semibold text-white transition hover:bg-primary-dark"
                >
                  Open AI Chat
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>

            {/* Account Information */}
            <div className="mt-8 rounded-2xl border border-border bg-white p-6">
              <h3 className="text-base font-semibold">
                Account information
              </h3>

              <div className="mt-5 grid gap-5 sm:grid-cols-2">
                <div>
                  <p className="text-xs text-muted">
                    Full name
                  </p>
                  <p className="mt-1 text-sm font-medium">
                    {user.full_name || "Not provided"}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted">
                    Email address
                  </p>
                  <p className="mt-1 break-all text-sm font-medium">
                    {user.email}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted">
                    Account status
                  </p>
                  <p className="mt-1 text-sm font-medium text-green-700">
                    {user.is_active ? "Active" : "Inactive"}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted">
                    Authentication
                  </p>
                  <p className="mt-1 text-sm font-medium">
                    Google OAuth
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
