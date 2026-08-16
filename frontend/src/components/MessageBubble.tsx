import ReactMarkdown from "react-markdown";
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
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                  strong: ({ children }) => (
                    <strong className="font-semibold text-leadtech-charcoal">{children}</strong>
                  ),
                  ul: ({ children }) => (
                    <ul className="my-2 flex flex-col gap-1.5 pl-5 list-disc marker:text-leadtech-red">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="my-2 flex flex-col gap-1.5 pl-5 list-decimal marker:text-leadtech-red">{children}</ol>
                  ),
                  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser && message.sourceDocuments && message.sourceDocuments.length > 0 && (
          <SourceBadges sources={message.sourceDocuments} />
        )}
      </div>
    </div>
  );
}
