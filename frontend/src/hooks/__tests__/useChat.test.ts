import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import * as apiModule from "../../services/api";
import { useChat } from "../useChat";

describe("useChat hook", () => {
  it("initializes with empty state", () => {
    const { result } = renderHook(() => useChat());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles successful sendMessage flow", async () => {
    const spy = vi.spyOn(apiModule, "sendChatMessage").mockResolvedValue({
      response: "There are 3 indexed candidate CVs.",
      source_documents: [
        { file_name: "jane.pdf", candidate_name: "Jane Doe" },
      ],
    });

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("How many candidates?");
    });

    expect(spy).toHaveBeenCalledWith("How many candidates?");
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toMatchObject({
      role: "user",
      content: "How many candidates?",
    });
    expect(result.current.messages[1]).toMatchObject({
      role: "assistant",
      content: "There are 3 indexed candidate CVs.",
      sourceDocuments: [{ file_name: "jane.pdf", candidate_name: "Jane Doe" }],
    });
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles error during sendMessage and clearError", async () => {
    vi.spyOn(apiModule, "sendChatMessage").mockRejectedValue(
      new apiModule.ChatApiError("Server Unavailable", 503)
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("Hello");
    });

    expect(result.current.error).toBe("Server Unavailable");
    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });
});
