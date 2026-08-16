import type { ApiError, ChatRequest, ChatResponse } from "../types/chat";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ChatApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ChatApiError";
    this.status = status;
  }
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const payload: ChatRequest = { message };

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorBody = (await response.json()) as ApiError;
      if (errorBody.detail) {
        errorMessage = errorBody.detail;
      }
    } catch {
      // Keep default message when error body is not JSON.
    }
    throw new ChatApiError(errorMessage, response.status);
  }

  return (await response.json()) as ChatResponse;
}
