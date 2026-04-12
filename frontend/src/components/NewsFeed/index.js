import React from "react";
import NewsCard from "../NewsCard";

export default function NewsFeed({ news, loading, error, pagination, onLoadMore }) {
  if (loading && news.length === 0) {
    return <div className="loading-spinner">Загрузка новостей...</div>;
  }

  if (error) {
    return <div className="error-message">Ошибка загрузки: {error}</div>;
  }

  if (news.length === 0) {
    return (
      <div className="empty-state">
        <p>Нет новостей за выбранный период.</p>
        <p className="empty-hint">Попробуйте расширить фильтры.</p>
      </div>
    );
  }

  return (
    <div className="news-feed">
      {news.map((article) => (
        <NewsCard key={article.id} news={article} />
      ))}

      {pagination.next && (
        <button className="load-more-btn" onClick={onLoadMore}>
          Загрузить ещё
        </button>
      )}
    </div>
  );
}
