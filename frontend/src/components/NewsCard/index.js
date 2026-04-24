import React from "react";
import { Link } from "react-router-dom";
import Badge from "./Badge";
import { cn } from "../../utils/cn";

export default function NewsCard({ news, className }) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const borderColors = {
    HIGH: "border-l-red-500",
    MEDIUM: "border-l-yellow-500",
    LOW: "border-l-green-500",
  };

  return (
    <article
      className={cn(
        "relative flex flex-col rounded-xl border border-l-4 bg-card p-4 text-card-foreground shadow-sm transition-colors hover:shadow-md",
        borderColors[news.significance_level] || borderColors.LOW,
        className
      )}
      data-testid="news-card"
    >
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
        <Badge level={news.significance_level} />
        <time>{formatDate(news.published_at)}</time>
        <span>·</span>
        <span className="font-medium">{news.source?.name}</span>
      </div>

      <Link to={`/news/${news.id}`} className="group">
        <h3 className="font-semibold leading-tight group-hover:text-primary transition-colors">
          {news.title}
        </h3>
      </Link>

      {news.summary && (
        <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
          {news.summary}
        </p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {news.category && (
          <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground">
            {news.category.name}
          </span>
        )}
        {news.assets?.slice(0, 3).map((asset) => (
          <span
            key={asset}
            className="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-semibold text-purple-700"
          >
            {asset}
          </span>
        ))}
      </div>
    </article>
  );
}
