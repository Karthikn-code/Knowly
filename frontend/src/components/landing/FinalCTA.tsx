
import Link from "next/link";
import { ArrowRight, Sparkles, ShieldCheck } from "lucide-react";

export default function FinalCTA() {
  return (
    <section className="px-6 py-24 lg:px-8">
      <div className="relative mx-auto max-w-7xl overflow-hidden rounded-3xl bg-gradient-to-br from-[#6845e8] to-[#5030c9] px-7 py-16 text-center shadow-xl shadow-purple-200 sm:px-12 sm:py-20">
        <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />

        <div className="pointer-events-none absolute -bottom-32 -left-20 h-72 w-72 rounded-full bg-purple-300/20 blur-3xl" />

        <div className="relative mx-auto max-w-3xl">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-white">
            <Sparkles size={28} />
          </div>

          <h2 className="mt-7 text-3xl font-bold tracking-tight text-white sm:text-5xl">
            Ready to work smarter with your documents?
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-purple-100 sm:text-lg">
            Discover a simpler way to understand your documents, find
            information, and get useful insights with AI.
          </p>

          <Link
            href="/get-started"
            className="mt-9 inline-flex items-center justify-center gap-3 rounded-xl bg-white px-7 py-4 font-semibold text-primary shadow-lg transition-all hover:-translate-y-1 hover:bg-purple-50"
          >
            Get Started with Knowly
            <ArrowRight size={18} />
          </Link>

          <div className="mt-7 flex items-center justify-center gap-2 text-sm text-purple-100">
            <ShieldCheck size={17} />
            Privacy-focused document assistance
          </div>
        </div>
      </div>
    </section>
  );
}
