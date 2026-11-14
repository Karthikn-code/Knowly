
import {
  FileSearch,
  MessageSquareText,
  Quote,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    icon: FileSearch,
    title: "Smart Document Analysis",
    description:
      "Upload your documents and let AI understand their content, structure, and important information.",
  },
  {
    icon: MessageSquareText,
    title: "AI-Powered Chat",
    description:
      "Ask questions in natural language and get relevant answers based on your uploaded documents.",
  },
  {
    icon: Quote,
    title: "Accurate Source References",
    description:
      "Explore the pages and sections behind AI-generated answers so you can verify the information.",
  },
  {
    icon: ShieldCheck,
    title: "Private Workspace",
    description:
      "Your documents remain private, with access restricted to your authenticated account.",
  },
];

export default function Features() {
  return (
    <section id="features" className="bg-[#faf9ff] px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <span className="inline-block rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-primary">
            Powerful Features
          </span>

          <h2 className="mt-5 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
            Everything you need to work smarter with documents
          </h2>

          <p className="mt-5 text-lg leading-8 text-gray-600">
            Knowly brings document understanding and AI-powered conversations
            together in one simple workspace.
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <article
                key={feature.title}
                className="group rounded-2xl border border-gray-100 bg-white p-7 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:border-purple-200 hover:shadow-xl hover:shadow-purple-100/50"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-50 text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                  <Icon size={27} strokeWidth={1.8} />
                </div>

                <h3 className="mt-7 text-lg font-bold text-gray-900">
                  {feature.title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-gray-600">
                  {feature.description}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
