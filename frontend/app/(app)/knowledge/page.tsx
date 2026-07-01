export default function KnowledgePage() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
          <p className="text-sm text-gray-500 mt-1">
            Upload your organisation&apos;s documents to power AI-generated applications.
          </p>
        </div>
        <button className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700">
          + Upload document
        </button>
      </div>
      {/* Document type sections */}
      {[
        { type: "annual_report", label: "Annual Reports" },
        { type: "strategic_plan", label: "Strategic Plans" },
        { type: "past_application", label: "Past Applications" },
        { type: "financial", label: "Financial Statements" },
        { type: "policy", label: "Policies & Programs" },
      ].map((section) => (
        <section key={section.type} className="mb-8">
          <h2 className="font-semibold text-gray-800 mb-3">{section.label}</h2>
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center">
            <p className="text-sm text-gray-400">
              Drag and drop files here, or click Upload document above.
            </p>
          </div>
        </section>
      ))}
    </div>
  );
}
