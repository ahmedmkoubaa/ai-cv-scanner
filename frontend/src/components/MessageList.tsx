import type { ChatMessage } from "../types/chat";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-leadtech-red/10">
          <span className="text-2xl font-semibold text-leadtech-red">;</span>
        </div>
        <h2 className="text-lg font-semibold text-leadtech-charcoal">
          Start your candidate search
        </h2>
        <p className="mt-2 max-w-md text-sm text-zinc-600">
          Ask about skills, experience, or backgrounds — we&apos;ll search the
          indexed CVs and cite the sources behind every answer.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-6 sm:px-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && <TypingIndicator />}
    </div>
  );
}
