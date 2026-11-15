import Image from "next/image";
import Link from "next/link";

const GOOGLE_LOGIN_URL = "/api/v1/auth/google/login";

const features = [
{
number: "01",
title: "Your documents, understood",
description: "Bring your learning materials together in one place.",
},
{
number: "02",
title: "Ask questions, get answers",
description: "Explore your documents with the help of AI.",
},
{
number: "03",
title: "Learn with confidence",
description: "Get clear answers supported by document references.",
},
];

export default function LoginPage() {
return (
<main className="relative min-h-screen overflow-hidden bg-[#f5f7fc]">
{/* Background decoration */}
<div className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-blue-200/30 blur-3xl" />
<div className="pointer-events-none absolute -bottom-40 -right-32 h-96 w-96 rounded-full bg-violet-200/30 blur-3xl" />

  <div className="relative mx-auto flex min-h-screen w-full max-w-[1440px] items-center justify-center px-5 py-8 sm:px-8 lg:px-12">
    <div className="grid w-full max-w-6xl overflow-hidden rounded-[28px] border border-white/80 bg-white shadow-[0_24px_80px_-24px_rgba(30,41,59,0.18)] lg:min-h-[650px] lg:grid-cols-2">

      {/* Left: Knowly introduction */}
      <section className="relative flex flex-col justify-between overflow-hidden bg-[#101b3d] px-7 py-9 text-white sm:px-10 sm:py-12 lg:px-12 lg:py-14">
        {/* Decorative background shapes */}
        <div className="pointer-events-none absolute -right-24 -top-20 h-80 w-80 rounded-full border border-white/10" />
        <div className="pointer-events-none absolute -right-12 -top-8 h-56 w-56 rounded-full border border-white/10" />
        <div className="pointer-events-none absolute -bottom-32 -left-20 h-80 w-80 rounded-full bg-blue-500/10 blur-2xl" />

        <div className="relative z-10">
          <Link href="/" className="inline-flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-lg shadow-black/10">
              <Image
                src="/icon.png"
                alt="Knowly Logo"
                width={38}
                height={38}
                className="h-9 w-9 object-contain"
              />
            </div>
            <span className="text-2xl font-bold tracking-tight">
              Knowly
            </span>
          </Link>

          <div className="mt-14 max-w-md sm:mt-20 lg:mt-24">
            <span className="inline-flex items-center gap-2 rounded-full border border-blue-300/20 bg-blue-400/10 px-3.5 py-1.5 text-xs font-medium tracking-wide text-blue-200">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-300" />
              YOUR AI LEARNING COMPANION
            </span>

            <h1 className="mt-7 text-4xl font-bold leading-[1.15] tracking-tight sm:text-5xl">
              Turn your
              <span className="block bg-gradient-to-r from-blue-300 to-violet-300 bg-clip-text text-transparent">
                documents
              </span>
              into knowledge.
            </h1>

            <p className="mt-6 max-w-sm text-sm leading-7 text-slate-300 sm:text-base">
              Meet a smarter way to learn. Upload your documents, ask
              questions, and discover the answers hidden in your study
              materials.
            </p>
          </div>

          <div className="mt-12 space-y-6 sm:mt-14">
            {features.map((feature) => (
              <div key={feature.number} className="flex gap-4">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-xs font-semibold text-blue-200">
                  {feature.number}
                </div>
                <div>
                  <h2 className="text-sm font-semibold text-white">
                    {feature.title}
                  </h2>
                  <p className="mt-1 text-xs leading-5 text-slate-400 sm:text-sm">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 mt-12 border-t border-white/10 pt-6">
          <p className="text-xs text-slate-400">
            A better way to understand what you learn.
          </p>
        </div>
      </section>

      {/* Right: Authentication */}
      <section className="flex flex-col justify-center px-7 py-12 sm:px-12 lg:px-14">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-10">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
              GET STARTED
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Welcome back.
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-500">
              Sign in or create your account to continue your learning
              journey with Knowly.
            </p>
          </div>

          {/* Google Authentication */}
          <a
            href={GOOGLE_LOGIN_URL}
            className="group flex w-full items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-800 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:bg-slate-50 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-blue-100"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 48 48"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path
                fill="#EA4335"
                d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5Z"
              />
              <path
                fill="#4285F4"
                d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.75 7.18l7.26 5.64c4.23-3.9 7.53-9.65 7.53-17.29Z"
              />
              <path
                fill="#FBBC05"
                d="M10.53 28.59A14.4 14.4 0 0 1 9.75 24c0-1.59.27-3.13.76-4.59l-7.98-6.19A23.9 23.9 0 0 0 0 24c0 3.87.93 7.54 2.56 10.78l7.97-6.19Z"
              />
              <path
                fill="#34A853"
                d="M24 48c6.48 0 11.93-2.13 15.9-5.8l-7.26-5.64c-2.02 1.35-4.6 2.14-8.64 2.14-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48Z"
              />
            </svg>

            Continue with Google

            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="ml-auto h-4 w-4 text-slate-400 transition-transform group-hover:translate-x-1"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 12h14m-7-7 7 7-7 7"
              />
            </svg>
          </a>

          <div className="my-8 flex items-center gap-4">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
              Simple and secure
            </span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          {/* Account information */}
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  className="h-4 w-4"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 5v14m-7-7h14"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">
                  New to Knowly?
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Your account will be created automatically when you
                  continue with Google.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  className="h-4 w-4"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 12.5 9.5 17 19 7"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">
                  Already have an account?
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Use the same Google account to sign in and access your
                  documents.
                </p>
              </div>
            </div>
          </div>

          {/* Security notice */}
          <div className="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-start gap-3">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m9 12 2 2 4-4"
                />
              </svg>
              <div>
                <p className="text-xs font-semibold text-slate-800">
                  Secure Google authentication
                </p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Your sign-in is handled securely through Google. No
                  Knowly password is required.
                </p>
              </div>
            </div>
          </div>

          {/* Back to home */}
          <div className="mt-9 text-center">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 transition hover:text-blue-600"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="h-4 w-4"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m15 18-6-6 6-6"
                />
              </svg>
              Back to home
            </Link>
          </div>

          <p className="mt-8 text-center text-[11px] text-slate-400">
  © 2026 Knowly. Learn smarter, every day.
</p>
        </div>
      </section>
    </div>
  </div>
</main>

);
}