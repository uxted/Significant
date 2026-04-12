import { render, screen } from "@testing-library/react";
import NewsCard from "../NewsCard";

test("отображает заголовок и источник", () => {
  const news = {
    id: 1,
    title: "ЦБ повысил ставку",
    summary: "Совет директоров принял решение",
    significance_level: "HIGH",
    source: { id: 1, name: "ТАСС", url: "https://tass.ru" },
    category: { id: 1, code: "macro", name: "Макроэкономика" },
    published_at: "2026-03-15T14:30:00Z",
    assets: ["GAZP", "SBER"],
    original_url: "https://tass.ru/123",
  };

  render(<NewsCard news={news} />);

  expect(screen.getByText("ЦБ повысил ставку")).toBeInTheDocument();
  expect(screen.getByText("ТАСС")).toBeInTheDocument();
});

test("отображает уровень значимости HIGH красным цветом", () => {
  const news = {
    id: 1,
    title: "Test",
    significance_level: "HIGH",
    source: { name: "Test" },
    published_at: "2026-03-15T14:30:00Z",
    assets: [],
    original_url: "https://test.ru",
  };

  render(<NewsCard news={news} />);

  const badge = screen.getByTestId("significance-badge");
  expect(badge).toHaveClass("badge-high");
  expect(badge).toHaveTextContent("High");
});

test("отображает MEDIUM жёлтым", () => {
  const news = {
    id: 1,
    title: "Test",
    significance_level: "MEDIUM",
    source: { name: "Test" },
    published_at: "2026-03-15T14:30:00Z",
    assets: [],
    original_url: "https://test.ru",
  };

  render(<NewsCard news={news} />);

  const badge = screen.getByTestId("significance-badge");
  expect(badge).toHaveClass("badge-medium");
});

test("отображает LOW зелёным", () => {
  const news = {
    id: 1,
    title: "Test",
    significance_level: "LOW",
    source: { name: "Test" },
    published_at: "2026-03-15T14:30:00Z",
    assets: [],
    original_url: "https://test.ru",
  };

  render(<NewsCard news={news} />);

  const badge = screen.getByTestId("significance-badge");
  expect(badge).toHaveClass("badge-low");
});
