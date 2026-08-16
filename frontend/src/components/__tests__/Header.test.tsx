import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Header } from "../Header";

describe("Header component", () => {
  it("renders branding title and badge", () => {
    render(<Header />);
    expect(screen.getByText("Leadtech")).toBeInTheDocument();
    expect(screen.getByText("AI CV Assistant")).toBeInTheDocument();
    expect(screen.getByText("Leadtech Candidate Search")).toBeInTheDocument();
  });
});
