
import {
  ShieldCheck,
  LockKeyhole,
  UserRoundCheck,
  FileLock2,
  CheckCircle2,
} from "lucide-react";

const securityFeatures = [
  {
    icon: LockKeyhole,
    title: "Private Document Storage",
    description:
      "Your uploaded documents are designed to remain private and accessible only to your account.",
  },
  {
    icon: UserRoundCheck,
    title: "Secure Google Sign-In",
    description:
      "Sign in with your Google account using industry-standard authentication protocols.",
  },
  {
    icon: FileLock2,
    title: "Controlled Document Access",
    description:
      "Every document request will be checked to ensure users can access only their own files.",
  },
];

export default function Security() {
  return (
    <section
      id="security"
      className="scroll-mt-24 bg-[#faf9ff] px-6 py-24 lg:px-8"
    >
      <div className="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-2">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-primary">
            <ShieldCheck size={16} />
            Privacy & Security
          </span>

          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl lg:text-5xl">
            Your documents.
            <br />
            <span className="text-primary">Your privacy.</span>
            <br />
            Our priority.
          </h2>

          <p className="mt-6 max-w-xl text-lg leading-8 text-gray-600">
            Knowly is being designed with privacy and security at its core.
            Your workspace will include account-based access controls and
            secure document handling.
          </p>

          <div className="mt-8 space-y-4">
            {[
              "Private, account-specific document access",
              "Secure authentication and session management",
              "Protected document processing and retrieval",
            ].map((item) => (
              <div key={item} className="flex items-center gap-3">
                <CheckCircle2
                  size={20}
                  className="shrink-0 text-primary"
                />
                <span className="text-sm font-medium text-gray-700">
                  {item}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-purple-100 bg-white p-6 shadow-xl shadow-purple-100/40 sm:p-9">
          <div className="mb-8 flex items-center gap-4 rounded-2xl bg-purple-50 p-5">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-primary text-white">
              <ShieldCheck size={28} />
            </div>

            <div>
              <h3 className="font-bold text-gray-900">
                Built with Security in Mind
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Privacy-focused architecture
              </p>
            </div>
          </div>

          <div className="space-y-6">
            {securityFeatures.map((feature) => {
              const Icon = feature.icon;

              return (
                <div key={feature.title} className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-purple-50 text-primary">
                    <Icon size={22} />
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {feature.title}
                    </h4>
                    <p className="mt-2 text-sm leading-6 text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
