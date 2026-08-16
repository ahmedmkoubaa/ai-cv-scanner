import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../App";
import * as apiModule from "../services/api";

describe("App main component integration", () => {
  it("renders empty state initially and updates on user search", async () => {
    vi.spyOn(apiModule, "sendChatMessage").mockResolvedValue({
      response: "Maya Lin has React experience.",
      source_documents: [
        { file_name: "maya_lin.pdf", candidate_name: "Maya Lin" },
      ],
    });

    render(<App />);

    expect(screen.getByText("Start your candidate search")).toBeInTheDocument();

    const input = screen.getByRole("textbox", { name: /chat message/i });
    fireEvent.change(input, { target: { value: "Who knows React?" } });

    const button = screen.getByRole("button", { name: /search/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Maya Lin has React experience.")).toBeInTheDocument();
    });

    expect(screen.getByText("maya_lin.pdf")).toBeInTheDocument();
  });
});
