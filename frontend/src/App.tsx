import { ChatInput } from "./components/ChatInput";
import { ChatWindow } from "./components/ChatWindow";
import { Header } from "./components/Header";
import { MessageList } from "./components/MessageList";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, isLoading, error, sendMessage, clearError } = useChat();

  return (
    <div className="flex min-h-screen flex-col bg-leadtech-surface">
      <Header />

      <ChatWindow>
        {error && (
          <div
            className="mx-4 mt-4 flex items-start justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 sm:mx-6"
            role="alert"
          >
            <p className="text-sm text-red-800">{error}</p>
            <button
              type="button"
              onClick={clearError}
              className="shrink-0 text-xs font-semibold uppercase tracking-wide text-red-600 hover:text-red-800"
            >
              Dismiss
            </button>
          </div>
        )}

        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </ChatWindow>
    </div>
  );
}
