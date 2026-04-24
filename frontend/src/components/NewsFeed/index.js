import React from "react";
import NewsCard from "../NewsCard";

export default function NewsFeed({ news, loading, error, pagination, onLoadMore }) {
  if (loading && news.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-4 text-sm text-muted-foreground">Загрузка новостей...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
        <p className="text-sm font-medium">Ошибка загрузки: {error}</p>
      </div>
    );
  }

  if (news.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border bg-card p-12 text-center shadow-sm">
        <p className="text-lg font-medium">Нет новостей за выбранный период.</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Попробуйте расширить фильтры.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {news.map((article) => (
        <NewsCard key={article.id} news={article} />
      ))}

      {pagination.next && (
        <button
          className="inline-flex w-full items-center justify-center rounded-md text-sm font-medium transition-colors
            border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          onClick={onLoadMore}
        >
          Загрузить ещё
        </button>
      )}
    </div>
  );
}
