export default function DiscoverPage() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Discover Grants</h1>
      </div>
      {/* Filters row */}
      <div className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Search grants..."
          className="border rounded-lg px-4 py-2 text-sm flex-1 max-w-xs"
        />
        <select className="border rounded-lg px-3 py-2 text-sm">
          <option value="">All categories</option>
        </select>
        <select className="border rounded-lg px-3 py-2 text-sm">
          <option value="">All states</option>
          <option>NSW</option>
          <option>VIC</option>
          <option>QLD</option>
          <option>SA</option>
          <option>WA</option>
          <option>TAS</option>
          <option>ACT</option>
          <option>NT</option>
        </select>
      </div>
      {/* Grant feed — populated once backend is connected */}
      <div className="space-y-4">
        <EmptyState />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-16 text-gray-400">
      <p className="text-lg font-medium mb-2">No grants yet</p>
      <p className="text-sm">
        Grant discovery runs every 6 hours. Complete your organisation profile to start
        seeing matched grants.
      </p>
    </div>
  );
}
