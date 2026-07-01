import Link from "next/link";

const PIPELINE_STAGES = [
  { key: "drafting", label: "Drafting" },
  { key: "in_review", label: "In Review" },
  { key: "approved", label: "Approved" },
  { key: "submitted", label: "Submitted" },
  { key: "awarded", label: "Awarded" },
];

export default function ApplicationsPage() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
        <Link
          href="/applications/new"
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + New application
        </Link>
      </div>
      {/* Kanban board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {PIPELINE_STAGES.map((stage) => (
          <div key={stage.key} className="min-w-[240px] bg-gray-100 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">{stage.label}</h3>
            <p className="text-xs text-gray-400 text-center py-8">No applications</p>
          </div>
        ))}
      </div>
    </div>
  );
}
