
import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  FileText,
  BrainCircuit,
  BookOpenCheck,
  MessagesSquare,
  ShieldCheck,
  Upload,
  Sparkles,
  LockKeyhole,
  CheckCircle2,
} from "lucide-react";

const features = [
  {
    icon: Upload,
    title: "Upload your documents",
    description:
      "Bring your knowledge together. Upload PDF, DOCX, PPTX, XLSX and TXT files.",
  },
  {
    icon: BrainCircuit,
    title: "Ask questions with AI",
    description:
      "Ask questions in natural language and receive answers based on your documents.",
  },
  {
    icon: BookOpenCheck,
    title: "Get answers with references",
    description:
      "Understand where information comes from with supporting document citations.",
  },
  {
    icon: MessagesSquare,
    title: "Continue your conversations",
    description:
      "Keep your conversations organised and return to previous discussions.",
  },
];

const steps = [
  {
    number: "01",
    title: "Upload",
    description: "Upload the documents you want to understand.",
  },
  {
    number: "02",
    title: "Ask",
    description: "Ask Knowly questions about your uploaded content.",
  },
  {
    number: "03",
    title: "Understand",
    description: "Explore AI-generated answers with relevant references.",
  },
];

export default function GetStartedPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-white">
      {/* Navigation */}
      <header className="border-b border-gray-100 bg-white">
        <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <Image
              src="/icon.png"
              alt="Knowly Logo"
              width={42}
              height={42}
              className="h-10 w-10 object-contain"
            />
            <span className="text-2xl font-bold tracking-tight text-gray-900">
              Knowly<span className="text-primary">.</span>
            </span>
          </Link>

          <Link
            href="/login"
            className="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:border-primary hover:text-primary"
          >
            Sign In
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-purple-50 via-white to-white px-6 py-20 sm:py-28">
        <div className="pointer-events-none absolute -right-40 -top-32 h-96 w-96 rounded-full bg-purple-200/40 blur-3xl" />
        <div className="pointer-events-none absolute -left-40 bottom-0 h-80 w-80 rounded-full bg-blue-100/50 blur-3xl" />

        <div className="relative mx-auto max-w-4xl text-center">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-purple-100 bg-white px-4 py-2 text-sm font-medium text-primary shadow-sm">
            <Sparkles size={16} />
            Your personal AI-powered learning companion
          </div>

          <h1 className="text-4xl font-bold leading-tight tracking-tight text-gray-950 sm:text-6xl">
            Get Started with{" "}
            <span className="text-primary">Knowly</span>
          </h1>

          <p className="mx-auto mt-7 max-w-2xl text-base leading-8 text-gray-600 sm:text-lg">
            Turn your documents into knowledge. Upload your files, ask
            questions, and discover information through an intelligent
            AI-powered document assistant.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/login"
              className="inline-flex w-full items-center justify-center gap-3 rounded-xl bg-primary px-8 py-4 font-semibold text-white shadow-lg shadow-purple-200 transition hover:-translate-y-1 hover:bg-primary-dark sm:w-auto"
            >
              Continue with Google
              <ArrowRight size={19} />
            </Link>

            <Link
              href="#how-it-works"
              className="inline-flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white px-8 py-4 font-semibold text-gray-700 transition hover:border-primary hover:text-primary sm:w-auto"
            >
              Explore How It Works
            </Link>
          </div>

          <div className="mt-7 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm text-gray-500">
            <span className="flex items-center gap-2">
              <ShieldCheck size={17} className="text-primary" />
              Private documents
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 size={17} className="text-primary" />
              AI-powered assistance
            </span>
            <span className="flex items-center gap-2">
              <LockKeyhole size={17} className="text-primary" />
              Secure Google sign-in
            </span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-sm font-semibold uppercase tracking-wider text-primary">
              Discover Knowly
            </span>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
              Everything you need to understand your documents
            </h2>
            <p className="mt-5 leading-7 text-gray-600">
              Knowly brings your documents and AI-powered assistance together
              in one place.
            </p>
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon;

              return (
                <div
                  key={feature.title}
                  className="rounded-2xl border border-gray-100 bg-white p-7 shadow-sm transition hover:-translate-y-1 hover:border-purple-100 hover:shadow-lg"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-primary">
                    <Icon size={24} />
                  </div>

                  <h3 className="mt-6 text-lg font-bold text-gray-900">
                    {feature.title}
                  </h3>

                  <p className="mt-3 text-sm leading-7 text-gray-600">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section
        id="how-it-works"
        className="bg-gray-50 px-6 py-20 lg:px-8"
      >
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-sm font-semibold uppercase tracking-wider text-primary">
              Simple workflow
            </span>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
              Get started in three simple steps
            </h2>
            <p className="mt-5 leading-7 text-gray-600">
              From uploading your documents to understanding their content,
              Knowly keeps the experience simple.
            </p>
          </div>

          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {steps.map((step) => (
              <div
                key={step.number}
                className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm"
              >
                <span className="text-4xl font-bold text-purple-200">
                  {step.number}
                </span>
                <h3 className="mt-5 text-xl font-bold text-gray-900">
                  {step.title}
                </h3>
                <p className="mt-3 leading-7 text-gray-600">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy */}
      <section className="px-6 py-20 lg:px-8">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 rounded-3xl border border-purple-100 bg-purple-50/60 px-7 py-12 text-center sm:px-12">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-primary shadow-sm">
            <ShieldCheck size={28} />
          </div>

          <h2 className="text-2xl font-bold text-gray-950 sm:text-3xl">
            Your knowledge deserves privacy
          </h2>

          <p className="max-w-2xl leading-7 text-gray-600">
            Knowly uses secure Google authentication and keeps your uploaded
            documents private to your account.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-6 pb-24 lg:px-8">
        <div className="relative mx-auto max-w-7xl overflow-hidden rounded-3xl bg-gradient-to-br from-[#6845e8] to-[#5030c9] px-7 py-16 text-center shadow-xl shadow-purple-200 sm:px-12 sm:py-20">
          <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />

          <div className="relative mx-auto max-w-3xl">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-white">
              <FileText size={28} />
            </div>

            <h2 className="mt-7 text-3xl font-bold tracking-tight text-white sm:text-5xl">
              Ready to explore your documents differently?
            </h2>

            <p className="mx-auto mt-6 max-w-2xl leading-8 text-purple-100">
              Start your journey with Knowly and experience a smarter way to
              work with your documents.
            </p>

            <Link
              href="/login"
              className="mt-9 inline-flex items-center justify-center gap-3 rounded-xl bg-white px-8 py-4 font-semibold text-primary shadow-lg transition hover:-translate-y-1 hover:bg-purple-50"
            >
              Continue with Google
              <ArrowRight size={18} />
            </Link>

            <p className="mt-6 text-sm text-purple-100">
              New to Knowly? Your account will be created automatically.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 px-6 py-7">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 text-sm text-gray-500 sm:flex-row">
          <Link href="/" className="font-semibold text-gray-800">
            Knowly<span className="text-primary">.</span>
          </Link>
          <p>Your personal AI-powered learning companion.</p>
          <Link href="/" className="transition hover:text-primary">
            Back to home
          </Link>
        </div>
      </footer>
    </main>
  );
}
