import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChatInput } from "../ChatInput";

describe("ChatInput component", () => {
  it("renders input field and search button", () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} />);
    const input = screen.getByRole("textbox", { name: /chat message/i });
    const button = screen.getByRole("button", { name: /search/i });

    expect(input).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it("submits typed query and clears input", () => {
    const onSendMock = vi.fn();
    render(<ChatInput onSend={onSendMock} isLoading={false} />);
    const input = screen.getByRole("textbox", { name: /chat message/i });

    fireEvent.change(input, { target: { value: "Who knows React?" } });
    const button = screen.getByRole("button", { name: /search/i });
    expect(button).not.toBeDisabled();

    fireEvent.click(button);
    expect(onSendMock).toHaveBeenCalledWith("Who knows React?");
    expect(input).toHaveValue("");
  });

  it("disables input and button when isLoading is true", () => {
    render(<ChatInput onSend={vi.fn()} isLoading={true} />);
    const input = screen.getByRole("textbox", { name: /chat message/i });
    const button = screen.getByRole("button", { name: /searching…/i });

    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
});
