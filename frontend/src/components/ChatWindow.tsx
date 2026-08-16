import type { ReactNode } from "react";

interface ChatWindowProps {
  children: ReactNode;
}

export function ChatWindow({ children }: ChatWindowProps) {
  return (
    <main className="mx-auto flex min-h-[calc(100vh-140px)] max-w-4xl flex-col px-4 py-6 sm:px-6">
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-card">
        {children}
      </div>
    </main>
  );
}
