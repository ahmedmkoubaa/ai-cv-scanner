import { FormEvent, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim() || isLoading) {
      return;
    }
    onSend(input);
    setInput("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-zinc-200 bg-white px-4 py-4 sm:px-6"
    >
      <div className="flex items-center gap-3">
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about candidates, skills, or experience…"
          disabled={isLoading}
          className="focus-ring-leadtech flex-1 rounded-full border border-zinc-300 bg-leadtech-surface px-5 py-3 text-sm text-leadtech-charcoal placeholder:text-zinc-400 disabled:cursor-not-allowed disabled:opacity-60 sm:text-base"
          aria-label="Chat message"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="focus-ring-leadtech shrink-0 rounded-full bg-leadtech-red px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-zinc-300 sm:px-6 sm:text-base"
        >
          {isLoading ? "Searching…" : "Search"}
        </button>
      </div>
    </form>
  );
}
