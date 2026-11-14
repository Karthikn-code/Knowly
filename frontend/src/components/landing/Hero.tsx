
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  FileText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import DashboardPreview from "./DashboardPreview";

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-white">
      {/* Background decoration */}
      <div className="pointer-events-none absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-purple-100/60 blur-3xl" />

      <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-6 py-20 lg:grid-cols-2 lg:px-8 lg:py-28">
        {/* Left content */}
        <div className="max-w-2xl">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-purple-100 bg-purple-50 px-4 py-2 text-sm font-medium text-primary">
            <Sparkles size={16} />
            Your smarter way to work with documents
          </div>

          <h1 className="text-5xl font-bold leading-[1.12] tracking-tight text-gray-950 sm:text-6xl lg:text-[64px]">
            Chat with your documents using{" "}
            <span className="text-primary">AI</span>
          </h1>

          <p className="mt-7 max-w-xl text-lg leading-8 text-gray-600">
            Upload your documents, ask questions in natural language, and get
            accurate answers with references. Make your documents work smarter
            with Knowly.
          </p>

          {/* Call to action */}
          <div className="mt-9 flex flex-col gap-4 sm:flex-row">
            <Link
              href="/get-started"
              className="inline-flex items-center justify-center gap-3 rounded-xl bg-primary px-7 py-4 font-semibold text-white shadow-lg shadow-purple-200 transition-all hover:-translate-y-1 hover:bg-primary-dark"
            >
              <svg
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
                  d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.72 7.18l7.62 5.91c4.45-4.1 7.14-10.15 7.14-17.56Z"
                />
                <path
                  fill="#FBBC05"
                  d="M10.53 28.59A14.4 14.4 0 0 1 9.75 24c0-1.59.27-3.13.76-4.59l-7.98-6.19A23.9 23.9 0 0 0 0 24c0 3.88.93 7.55 2.56 10.78l7.97-6.19Z"
                />
                <path
                  fill="#34A853"
                  d="M24 48c6.48 0 11.93-2.13 15.84-5.89l-7.62-5.91c-2.11 1.41-4.82 2.25-8.22 2.25-6.26 0-11.57-4.22-13.47-9.91l-7.97 6.19C6.51 42.62 14.62 48 24 48Z"
                />
              </svg>

              Get Started with Knowly
              <ArrowRight size={18} />
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-gray-500">
            <span className="flex items-center gap-2">
              <ShieldCheck size={17} className="text-primary" />
              Private documents
            </span>

            <span className="flex items-center gap-2">
              <CheckCircle2 size={17} className="text-primary" />
              AI-powered answers
            </span>
          </div>

          <div className="mt-8 flex items-center gap-3 border-t border-gray-100 pt-6">
            <div className="flex -space-x-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-purple-100">
                <FileText size={16} className="text-primary" />
              </div>

              <div className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-blue-100">
                <FileText size={16} className="text-blue-600" />
              </div>

              <div className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-pink-100">
                <FileText size={16} className="text-pink-600" />
              </div>
            </div>

            <p className="text-sm text-gray-500">
              Works with PDF, DOCX, PPTX, XLSX and TXT
            </p>
          </div>
        </div>

        {/* Right dashboard preview */}
        <div className="relative mx-auto w-full max-w-xl">
          <DashboardPreview />
        </div>
      </div>
    </section>
  );
}
