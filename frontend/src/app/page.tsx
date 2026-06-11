export default function Home() {
  return (
    <main className="min-h-screen bg-background px-6 py-16 text-foreground sm:px-10">
      <section className="mx-auto flex max-w-3xl flex-col gap-8">
        <div className="space-y-4">
          <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
            Autonomous Site Starter
          </p>
          <h1 className="text-4xl font-semibold tracking-normal text-balance sm:text-5xl">
            Project ready
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-zinc-600">
            Fill in PRODUCT.md and DESIGN.md, create the first task, then start
            building the site from approved scope.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {["Define product", "Choose direction", "Create task"].map((item) => (
            <div key={item} className="rounded-lg border border-zinc-200 bg-white p-5">
              <p className="text-sm font-medium text-zinc-900">{item}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
