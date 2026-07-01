export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard label="New grants matched" value="—" />
        <StatCard label="Applications in progress" value="—" />
        <StatCard label="Upcoming deadlines" value="—" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white rounded-xl border p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Deadlines this week</h2>
          <p className="text-sm text-gray-400">No upcoming deadlines.</p>
        </section>
        <section className="bg-white rounded-xl border p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Recent activity</h2>
          <p className="text-sm text-gray-400">No recent activity.</p>
        </section>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border p-6">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
