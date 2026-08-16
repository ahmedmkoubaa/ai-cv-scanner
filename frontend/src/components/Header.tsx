export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200/80 bg-white/90 shadow-sm backdrop-blur-md transition-all">
      <div className="mx-auto flex max-w-4xl flex-col gap-4 px-4 py-4 sm:px-6 sm:py-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-semibold tracking-tight text-leadtech-charcoal">
                Leadtech
              </span>
              <span className="text-2xl font-semibold text-leadtech-red">;</span>
              <span
                className="mb-1 ml-1 inline-block h-2 w-2 rounded-full bg-leadtech-red"
                aria-hidden="true"
              />
            </div>
            <span className="rounded-full border border-leadtech-red/20 bg-leadtech-red/5 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-leadtech-red">
              AI CV Assistant
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-200/80 bg-leadtech-offwhite/80 px-4 py-3">
          <p className="text-sm leading-relaxed text-zinc-700 sm:text-base">
            <span className="font-semibold text-leadtech-charcoal">
              Leadtech Candidate Search
            </span>
            {" — "}
            Turning queries into hiring success in style.
          </p>
        </div>
      </div>
    </header>
  );
}
