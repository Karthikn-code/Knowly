
import {
  CloudUpload,
  MessageCircleQuestion,
  Lightbulb,
  ArrowRight,
  Sparkles,
} from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Upload Your Documents",
    description:
      "Upload PDFs, Word documents, presentations, spreadsheets, and text files to your private Knowly workspace.",
    icon: CloudUpload,
  },
  {
    number: "02",
    title: "Ask Your Questions",
    description:
      "Ask questions about your documents using natural language. Knowly understands the context and finds relevant information.",
    icon: MessageCircleQuestion,
  },
  {
    number: "03",
    title: "Get Intelligent Insights",
    description:
      "Receive AI-generated answers with source references so you can verify the information in your original documents.",
    icon: Lightbulb,
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="bg-white px-6 py-24 lg:px-8"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <span className="inline-block rounded-full bg-purple-50 px-4 py-2 text-sm font-semibold text-primary">
            Simple Workflow
          </span>

          <h2 className="mt-5 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
            Get more from your documents in three simple steps
          </h2>

          <p className="mt-5 text-lg leading-8 text-gray-600">
            From uploading documents to discovering useful information,
            Knowly makes the entire process simple.
          </p>
        </div>

        <div className="mt-16 grid gap-8 lg:grid-cols-3">
          {steps.map((step, index) => {
            const Icon = step.icon;

            return (
              <div key={step.number} className="relative">
                <article className="h-full rounded-2xl border border-gray-100 bg-[#faf9ff] p-8 transition-all duration-300 hover:-translate-y-2 hover:border-purple-200 hover:shadow-xl hover:shadow-purple-100/50">
                  <div className="flex items-center justify-between">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-100 text-primary">
                      <Icon size={27} strokeWidth={1.8} />
                    </div>

                    <span className="text-4xl font-bold text-purple-100">
                      {step.number}
                    </span>
                  </div>

                  <h3 className="mt-8 text-xl font-bold text-gray-900">
                    {step.title}
                  </h3>

                  <p className="mt-4 text-sm leading-7 text-gray-600">
                    {step.description}
                  </p>
                </article>

                {index !== steps.length - 1 && (
                  <div className="absolute -right-7 top-1/2 z-10 hidden -translate-y-1/2 text-purple-300 lg:block">
                    <ArrowRight size={24} />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-12 rounded-2xl border border-purple-100 bg-purple-50/70 p-6 sm:p-8">
          <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white text-primary shadow-sm">
              <Sparkles size={24} />
            </div>

            <div>
              <h3 className="font-bold text-gray-900">
                Your documents, made easier to understand.
              </h3>
              <p className="mt-1 text-sm text-gray-600">
                Spend less time searching and more time understanding.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
