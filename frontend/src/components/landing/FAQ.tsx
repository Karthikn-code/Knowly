"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

const questions = [
  {
    question: "What is Knowly?",
    answer:
      "Knowly is an AI document assistant designed to help you upload documents, ask questions about their contents, and receive answers with source references.",
  },
  {
    question: "Which document formats will Knowly support?",
    answer:
      "The initial supported formats are PDF, TXT, DOCX, PPTX and XLSX.",
  },
  {
    question: "How does document question answering work?",
    answer:
      "Knowly is being built with retrieval-augmented generation (RAG). It will retrieve relevant document content and use that context to generate answers.",
  },
  {
    question: "Will my documents be private?",
    answer:
      "Documents are intended to be private by default. Backend authorization will ensure that users can access only their own documents.",
  },
  {
    question: "Can I see where an answer came from?",
    answer:
      "Knowly is designed to provide source references, such as PDF pages or presentation slides, so users can check the original information.",
  },
  {
    question: "Can I use my existing Google account?",
    answer:
      "Yes. Knowly is planned to support Google sign-in, with user accounts created automatically on their first successful sign-in.",
  },
];

export default function FAQ() {
  const [activeIndex, setActiveIndex] = useState<number | null>(0);

  return (
    <section id="faq" className="scroll-mt-24 bg-[#faf9ff] px-6 py-24 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="text-center">
          <span className="inline-block rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-primary">
            FAQ
          </span>

          <h2 className="mt-5 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
            Frequently asked questions
          </h2>

          <p className="mt-5 text-lg leading-8 text-gray-600">
            Learn more about Knowly and how it is being designed to work.
          </p>
        </div>

        <div className="mt-12 space-y-4">
          {questions.map((item, index) => {
            const isOpen = activeIndex === index;

            return (
              <div
                key={item.question}
                className="overflow-hidden rounded-2xl border border-gray-200 bg-white"
              >
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() =>
                    setActiveIndex(isOpen ? null : index)
                  }
                  className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                >
                  <span className="font-semibold text-gray-900">
                    {item.question}
                  </span>

                  <ChevronDown
                    size={20}
                    className={`shrink-0 text-primary transition-transform ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 px-6 py-5">
                    <p className="text-sm leading-7 text-gray-600">
                      {item.answer}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}