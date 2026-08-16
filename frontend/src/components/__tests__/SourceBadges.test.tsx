import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SourceBadges } from "../SourceBadges";

describe("SourceBadges component", () => {
  it("renders list of source document badges", () => {
    const sources = [
      { file_name: "maya_lin.pdf", candidate_name: "Maya Lin" },
      { file_name: "lars_lindqvist.pdf", candidate_name: "Lars Lindqvist" },
    ];
    render(<SourceBadges sources={sources} />);

    expect(screen.getByText("Sources")).toBeInTheDocument();
    expect(screen.getByText("Maya Lin")).toBeInTheDocument();
    expect(screen.getByText("maya_lin.pdf")).toBeInTheDocument();
    expect(screen.getByText("Lars Lindqvist")).toBeInTheDocument();
    expect(screen.getByText("lars_lindqvist.pdf")).toBeInTheDocument();
  });
});
