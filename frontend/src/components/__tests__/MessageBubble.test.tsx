import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MessageBubble } from "../MessageBubble";

describe("MessageBubble component", () => {
  it("renders user message as plain text", () => {
    render(
      <MessageBubble
        message={{
          id: "1",
          role: "user",
          content: "Show candidate names",
        }}
      />
    );
    expect(screen.getByText("Show candidate names")).toBeInTheDocument();
  });

  it("renders assistant message with markdown bold formatting and sources", () => {
    render(
      <MessageBubble
        message={{
          id: "2",
          role: "assistant",
          content: "* **Maya Lin**: Junior Frontend Developer",
          sourceDocuments: [
            { file_name: "maya_lin.pdf", candidate_name: "Maya Lin" },
          ],
        }}
      />
    );

    const mayaLinElements = screen.getAllByText("Maya Lin");
    const strongElement = mayaLinElements.find((el) => el.tagName === "STRONG");
    expect(strongElement).toBeDefined();
    expect(screen.getByText("maya_lin.pdf")).toBeInTheDocument();
  });
});
