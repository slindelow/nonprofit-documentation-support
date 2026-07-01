export default function CompliancePage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Compliance</h1>
      <p className="text-sm text-gray-500 mb-8">
        Track reporting obligations, milestones, and acquittal requirements for all awarded grants.
      </p>
      <div className="bg-white border rounded-xl p-6">
        <p className="text-sm text-gray-400 text-center py-12">
          No awarded grants yet. Compliance milestones will appear here once a grant is awarded
          and you upload the grant agreement.
        </p>
      </div>
    </div>
  );
}
