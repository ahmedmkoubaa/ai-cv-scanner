import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ChatApiError, sendChatMessage } from "../api";

describe("api service", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("sends chat message and returns response data", async () => {
    const mockResponse = {
      response: "Found 2 candidates.",
      source_documents: [
        { file_name: "maya_lin.pdf", candidate_name: "Maya Lin" },
      ],
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    } as unknown as Response);

    const result = await sendChatMessage("How many candidates?");

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/chat",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "How many candidates?" }),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  it("throws ChatApiError with server detail message when response is not ok", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => ({ detail: "LLM Provider Unavailable" }),
    } as unknown as Response);

    await expect(sendChatMessage("query")).rejects.toThrow(ChatApiError);
  });

  it("falls back to default error message if error body is not json", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("Invalid JSON");
      },
    } as unknown as Response);

    try {
      await sendChatMessage("query");
    } catch (err) {
      expect(err).toBeInstanceOf(ChatApiError);
      expect((err as ChatApiError).message).toBe("Request failed with status 500");
    }
  });
});
