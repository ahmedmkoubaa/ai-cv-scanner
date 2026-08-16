import type { SourceDocument } from "../types/chat";

interface SourceBadgesProps {
  sources: SourceDocument[];
}

export function SourceBadges({ sources }: SourceBadgesProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <span className="w-full text-xs font-medium uppercase tracking-wide text-zinc-500">
        Sources
      </span>
      {sources.map((source) => (
        <button
          key={`${source.file_name}-${source.candidate_name}`}
          type="button"
          title={source.file_name}
          className="group rounded-full border border-transparent bg-zinc-100 px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:border-leadtech-red hover:bg-white hover:text-leadtech-red focus-ring-leadtech"
        >
          <span className="font-semibold">{source.candidate_name}</span>
          <span className="mx-1 text-zinc-400 group-hover:text-leadtech-red/60">
            ·
          </span>
          <span className="text-zinc-500 group-hover:text-leadtech-red/80">
            {source.file_name}
          </span>
        </button>
      ))}
    </div>
  );
}
