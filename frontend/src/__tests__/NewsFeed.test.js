import { render, screen } from "@testing-library/react";
import NewsFeed from "../NewsFeed";

test("отображает список новостей", () => {
  const news = [
    {
      id: 1,
      title: "News 1",
      significance_level: "HIGH",
      source: { name: "Source 1" },
      published_at: "2026-03-15T14:30:00Z",
      assets: [],
      original_url: "https://test.ru/1",
    },
    {
      id: 2,
      title: "News 2",
      significance_level: "MEDIUM",
      source: { name: "Source 2" },
      published_at: "2026-03-15T13:30:00Z",
      assets: [],
      original_url: "https://test.ru/2",
    },
  ];

  render(
    <NewsFeed
      news={news}
      loading={false}
      error={null}
      pagination={{ count: 2, next: null, previous: null }}
      onLoadMore={() => {}}
    />
  );

  expect(screen.getByText("News 1")).toBeInTheDocument();
  expect(screen.getByText("News 2")).toBeInTheDocument();
});

test("отображает сообщение о пустой выдаче", () => {
  render(
    <NewsFeed
      news={[]}
      loading={false}
      error={null}
      pagination={{ count: 0, next: null, previous: null }}
      onLoadMore={() => {}}
    />
  );

  expect(screen.getByText("Нет новостей за выбранный период.")).toBeInTheDocument();
});

test("отображает состояние загрузки", () => {
  render(
    <NewsFeed
      news={[]}
      loading={true}
      error={null}
      pagination={{ count: 0, next: null, previous: null }}
      onLoadMore={() => {}}
    />
  );

  expect(screen.getByText("Загрузка новостей...")).toBeInTheDocument();
});

test("отображает сообщение об ошибке", () => {
  render(
    <NewsFeed
      news={[]}
      loading={false}
      error="Network error"
      pagination={{ count: 0, next: null, previous: null }}
      onLoadMore={() => {}}
    />
  );

  expect(screen.getByText("Ошибка загрузки: Network error")).toBeInTheDocument();
});
