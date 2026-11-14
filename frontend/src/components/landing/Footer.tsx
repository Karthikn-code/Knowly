import Link from "next/link";
import { FileText, GitBranch, Mail } from "lucide-react";
const footerLinks = [
  { name: "Features", href: "#features" },
  { name: "How It Works", href: "#how-it-works" },
  { name: "Security", href: "#security" },
  { name: "Pricing", href: "#pricing" },
  { name: "FAQ", href: "#faq" },
];

export default function Footer() {
  return (
    <footer className="border-t border-gray-100 bg-white px-6 pt-14 pb-8 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <Link href="/" className="inline-flex items-center gap-2.5">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white">
                <FileText size={22} />
              </div>

              <span className="text-2xl font-bold tracking-tight text-gray-900">
                Knowly<span className="text-primary">.</span>
              </span>
            </Link>

            <p className="mt-5 max-w-sm text-sm leading-7 text-gray-500">
              Your AI Document Assistant. A smarter way to understand,
              search and interact with your documents.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900">Explore</h3>

            <ul className="mt-5 space-y-3">
              {footerLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-gray-500 transition-colors hover:text-primary"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900">Get in touch</h3>

            <p className="mt-5 text-sm leading-7 text-gray-500">
              Have questions or feedback about Knowly?
            </p>

            <div className="mt-4 flex items-center gap-3 text-sm text-gray-600">
              <Mail size={17} className="text-primary" />
              Contact information coming soon
            </div>

            <div className="mt-4 flex items-center gap-3 text-sm text-gray-600">
              <GitBranch size={17} className="text-primary" />
              Project repository coming soon
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-gray-100 pt-7 text-sm text-gray-500 sm:flex-row sm:items-center sm:justify-between">
          <p>
  © 2026 Knowly. All rights reserved.
</p>

          <p>Your AI Document Assistant</p>
        </div>
      </div>
    </footer>
  );
}