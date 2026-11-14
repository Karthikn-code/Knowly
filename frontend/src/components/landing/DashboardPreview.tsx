
import {
  FileText,
  FileSpreadsheet,
  File,
  Search,
  Plus,
  MessageSquare,
  Sparkles,
  ArrowUp,
  PanelLeft,
  MoreHorizontal,
  CheckCircle2,
} from "lucide-react";

const documents = [
  {
    name: "Research_Paper.pdf",
    type: "PDF",
    size: "2.4 MB",
    icon: FileText,
    color: "text-red-500",
    bg: "bg-red-50",
  },
  {
    name: "Project_Report.docx",
    type: "DOCX",
    size: "1.8 MB",
    icon: File,
    color: "text-blue-500",
    bg: "bg-blue-50",
  },
  {
    name: "Financial_Data.xlsx",
    type: "XLSX",
    size: "940 KB",
    icon: FileSpreadsheet,
    color: "text-green-600",
    bg: "bg-green-50",
  },
];

export default function DashboardPreview() {
  return (
    <div className="relative rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl shadow-purple-100/70 sm:p-4">
      {/* Dashboard top bar */}
      <div className="flex items-center justify-between border-b border-gray-100 px-2 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
            <FileText size={17} />
          </div>
          <span className="font-bold text-gray-900">Knowly</span>
        </div>

        <div className="flex items-center gap-3 text-gray-400">
          <PanelLeft size={18} />
          <MoreHorizontal size={19} />
          <div className="h-8 w-8 rounded-full bg-purple-100" />
        </div>
      </div>

      <div className="grid grid-cols-[125px_1fr] gap-3 pt-4 sm:grid-cols-[155px_1fr]">
        {/* Sidebar */}
        <aside className="border-r border-gray-100 pr-3">
          <button className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-primary px-2 py-2.5 text-xs font-semibold text-white">
            <Plus size={14} />
            New Chat
          </button>

          <div className="mt-5 space-y-4">
            <div>
              <p className="mb-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Workspace
              </p>

              <div className="flex items-center gap-2 text-xs font-medium text-primary">
                <MessageSquare size={14} />
                My Documents
              </div>

              <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                <Search size={14} />
                Search Files
              </div>
            </div>

            <div>
              <p className="mb-3 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                Recent Files
              </p>

              {documents.map((doc) => {
                const Icon = doc.icon;

                return (
                  <div key={doc.name} className="mb-3 flex items-center gap-2">
                    <div className={`rounded-md p-1.5 ${doc.bg}`}>
                      <Icon size={13} className={doc.color} />
                    </div>

                    <p className="truncate text-[10px] text-gray-600">
                      {doc.name}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </aside>

        {/* Chat area */}
        <div className="min-w-0">
          <div className="mb-5">
            <h3 className="text-sm font-bold text-gray-900">
              Document Assistant
            </h3>
            <p className="mt-1 text-[10px] text-gray-400">
              Ask anything about your documents
            </p>
          </div>

          <div className="ml-auto max-w-[90%] rounded-xl bg-purple-50 p-3">
            <p className="text-[11px] leading-5 text-gray-700">
              Summarize the key findings from my research paper.
            </p>
          </div>

          <div className="mt-4 rounded-xl border border-gray-100 bg-gray-50/80 p-3">
            <div className="mb-2 flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-white">
                <Sparkles size={13} />
              </div>

              <span className="text-[11px] font-bold text-gray-800">
                Knowly AI
              </span>

              <span className="ml-auto text-[9px] text-green-600">
                <CheckCircle2 size={11} className="inline" /> Answer ready
              </span>
            </div>

            <p className="text-[11px] leading-5 text-gray-600">
              Based on your research paper, the key findings highlight three
              important areas of improvement and demonstrate promising results
              across the evaluated experiments.
            </p>

            <div className="mt-3 rounded-lg border border-purple-100 bg-white p-2">
              <p className="text-[9px] font-semibold text-primary">
                SOURCE REFERENCE
              </p>
              <p className="mt-1 text-[10px] text-gray-500">
                Research_Paper.pdf · Page 4
              </p>
            </div>
          </div>

          <div className="mt-5 flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-3">
            <p className="flex-1 text-[10px] text-gray-400">
              Ask a follow-up question...
            </p>

            <div className="rounded-lg bg-primary p-1.5 text-white">
              <ArrowUp size={13} />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom status */}
      <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-3">
        <span className="text-[9px] text-gray-400">
          AI-powered document intelligence
        </span>
        <span className="text-[9px] font-medium text-green-600">
          ● Secure workspace
        </span>
      </div>
    </div>
  );
}
