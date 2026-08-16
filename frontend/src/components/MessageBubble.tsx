import type { ChatMessage } from "../types/chat";
import { SourceBadges } from "./SourceBadges";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] sm:max-w-[75%] ${
          isUser ? "items-end" : "items-start"
        } flex flex-col gap-2`}
      >
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed sm:text-base ${
            isUser
              ? "rounded-br-md bg-leadtech-red font-medium text-white shadow-sm"
              : "rounded-bl-md border border-zinc-200 bg-leadtech-offwhite text-leadtech-charcoal"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {!isUser && message.sourceDocuments && message.sourceDocuments.length > 0 && (
          <SourceBadges sources={message.sourceDocuments} />
        )}
      </div>
    </div>
  );
}
