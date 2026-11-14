import { CheckCircle2, Sparkles } from "lucide-react";

const plannedFeatures = [
  "AI-powered document conversations",
  "Support for PDF, DOCX, PPTX, XLSX and TXT",
  "Answers with source references",
  "Private user workspace",
];

export default function Pricing() {
  return (
    <section id="pricing" className="scroll-mt-24 bg-white px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-4xl text-center">
        <span className="inline-flex items-center gap-2 rounded-full bg-purple-50 px-4 py-2 text-sm font-semibold text-primary">
          <Sparkles size={16} />
          Pricing
        </span>

        <h2 className="mt-5 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
          Simple access to smarter document workflows
        </h2>

        <p className="mt-5 text-lg leading-8 text-gray-600">
          We&apos;re shaping the right plans for individuals and teams. Pricing
          details will be announced when Knowly is ready to launch.
        </p>

        <div className="mx-auto mt-12 max-w-lg rounded-3xl border border-purple-200 bg-[#faf9ff] p-8 text-left shadow-lg shadow-purple-100/40 sm:p-10">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-900">
              Knowly
            </h3>
            <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-primary">
              Launch details pending
            </span>
          </div>

          <p className="mt-4 text-sm leading-7 text-gray-600">
            Explore the capabilities planned for the Knowly document
            assistant.
          </p>

          <div className="my-7 border-t border-purple-100" />

          <ul className="space-y-4">
            {plannedFeatures.map((feature) => (
              <li key={feature} className="flex items-start gap-3">
                <CheckCircle2
                  size={19}
                  className="mt-0.5 shrink-0 text-primary"
                />
                <span className="text-sm text-gray-700">{feature}</span>
              </li>
            ))}
          </ul>

          <p className="mt-8 rounded-xl bg-white p-4 text-center text-sm text-gray-500">
            Final plans, limits and pricing will be confirmed before launch.
          </p>
        </div>
      </div>
    </section>
  );
}