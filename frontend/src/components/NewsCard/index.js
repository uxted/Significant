import React from "react";
import { Link } from "react-router-dom";

const SIGNIFICANCE_CONFIG = {
  HIGH: { label: "High", className: "badge-high", icon: "🔴" },
  MEDIUM: { label: "Medium", className: "badge-medium", icon: "🟡" },
  LOW: { label: "Low", className: "badge-low", icon: "🟢" },
};

function SignificanceBadge({ level }) {
  const config = SIGNIFICANCE_CONFIG[level] || SIGNIFICANCE_CONFIG.LOW;
  return (
    <span className={`significance-badge ${config.className}`} data-testid="significance-badge">
      {config.icon} {config.label}
    </span>
  );
}

export default function NewsCard({ news }) {
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

  return (
    <article className="news-card" data-testid="news-card">
      <div className="news-card-header">
        <div className="news-card-meta">
          <SignificanceBadge level={news.significance_level} />
          <span className="news-time">{formatDate(news.published_at)}</span>
          <span className="news-source">{news.source?.name}</span>
        </div>
      </div>

      <Link to={`/news/${news.id}`} className="news-title-link">
        <h3 className="news-title">{news.title}</h3>
      </Link>

      {news.summary && (
        <p className="news-summary">{news.summary}</p>
      )}

      <div className="news-card-footer">
        {news.category && (
          <span className="news-category-tag">{news.category.name}</span>
        )}
        {news.assets && news.assets.length > 0 && (
          <div className="news-assets">
            {news.assets.slice(0, 3).map((asset) => (
              <span key={asset} className="asset-ticker">
                {asset}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
