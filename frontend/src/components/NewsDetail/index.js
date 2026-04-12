import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../../services/api";

export default function NewsDetail() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await api.get(`/api/news/${id}/`);
        setArticle(response.data);
      } catch (err) {
        setError("Не удалось загрузить новость");
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [id]);

  if (loading) return <div className="loading-spinner">Загрузка...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!article) return <div className="empty-state">Новость не найдена</div>;

  const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  const significanceIcons = { HIGH: "🔴", MEDIUM: "🟡", LOW: "🟢" };

  return (
    <article className="news-detail">
      <div className="news-detail-header">
        <span className={`significance-badge badge-${article.significance_level.toLowerCase()}`}>
          {significanceIcons[article.significance_level]} {article.significance_level}
        </span>
        <span className="news-source">{article.source?.name}</span>
        <span className="news-time">{formatDate(article.published_at)}</span>
      </div>

      <h1>{article.title}</h1>

      {article.category && (
        <span className="category-tag">{article.category.name}</span>
      )}

      <div className="news-detail-body">
        <p className="news-summary">{article.summary}</p>
        {article.full_text && (
          <div className="news-full-text">{article.full_text}</div>
        )}
      </div>

      {article.assets && article.assets.length > 0 && (
        <div className="news-assets">
          <h4>Затрагиваемые активы:</h4>
          <div className="asset-list">
            {article.assets.map((asset) => (
              <span key={asset} className="asset-ticker">
                {asset}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="news-detail-footer">
        <a
          href={article.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-original"
        >
          Читать полностью →
        </a>
        <Link to="/" className="btn-back">
          ← Назад к ленте
        </Link>
      </div>
    </article>
  );
}
