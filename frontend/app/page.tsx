import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      <nav className="flex items-center justify-between px-8 py-5 border-b">
        <span className="text-xl font-bold text-blue-600">GrantFlow AI</span>
        <div className="flex gap-4">
          <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900">
            Sign in
          </Link>
          <Link
            href="/signup"
            className="text-sm bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Get started
          </Link>
        </div>
      </nav>

      <section className="max-w-4xl mx-auto px-8 py-24 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Grant funding, on autopilot.
        </h1>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          GrantFlow AI finds relevant grants, drafts your applications using your
          organisation&apos;s own data, and keeps you on top of every deadline and
          reporting obligation.
        </p>
        <Link
          href="/signup"
          className="inline-block bg-blue-600 text-white text-lg px-8 py-4 rounded-lg hover:bg-blue-700 font-medium"
        >
          Start for free
        </Link>
        <p className="mt-4 text-sm text-gray-400">
          Built for Australian nonprofits and community organisations.
        </p>
      </section>

      <section className="max-w-5xl mx-auto px-8 pb-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        {[
          {
            title: "Discover grants",
            body: "AI surfaces grants from GrantConnect and other Australian funding sources matched to your mission.",
          },
          {
            title: "Draft applications",
            body: "Your organisation's knowledge base powers AI-generated applications — ready for your review.",
          },
          {
            title: "Never miss a deadline",
            body: "Automatic reminders for grant close dates, progress reports, and acquittals.",
          },
        ].map((f) => (
          <div key={f.title} className="p-6 border rounded-xl">
            <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
            <p className="text-gray-600 text-sm">{f.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
