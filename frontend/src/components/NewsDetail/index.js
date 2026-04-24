import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../../services/api";
import Badge from "../NewsCard/Badge";

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
      } catch {
        setError("Не удалось загрузить новость");
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [id]);

  if (loading)
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-sm text-muted-foreground">Загрузка...</p>
      </div>
    );
  if (error)
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
        {error}
      </div>
    );
  if (!article)
    return (
      <div className="text-center py-12 text-muted-foreground">
        Новость не найдена
      </div>
    );

  const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <article className="mx-auto max-w-3xl space-y-6 rounded-xl border bg-card p-8 shadow-sm">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <Badge level={article.significance_level} />
        <span className="font-medium">{article.source?.name}</span>
        <span>·</span>
        <time>{formatDate(article.published_at)}</time>
      </div>

      {/* Title */}
      <h1 className="text-3xl font-bold tracking-tight">{article.title}</h1>

      {article.category && (
        <span className="inline-flex items-center rounded-md bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground">
          {article.category.name}
        </span>
      )}

      {/* Body */}
      <div className="prose prose-sm max-w-none text-foreground leading-relaxed">
        <p className="text-lg font-medium text-muted-foreground">{article.summary}</p>
        {article.full_text && (
          <div className="mt-4 whitespace-pre-line">{article.full_text}</div>
        )}
      </div>

      {/* Assets */}
      {article.assets?.length > 0 && (
        <div className="rounded-lg border bg-muted/50 p-4">
          <h4 className="text-sm font-semibold mb-2">Затрагиваемые активы:</h4>
          <div className="flex flex-wrap gap-2">
            {article.assets.map((asset) => (
              <span
                key={asset}
                className="inline-flex items-center rounded-md bg-purple-50 px-2.5 py-1 text-xs font-semibold text-purple-700"
              >
                {asset}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex gap-4 pt-4 border-t">
        <a
          href={article.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
            bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
        >
          Читать полностью →
        </a>
        <Link
          to="/"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
            border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
        >
          ← Назад к ленте
        </Link>
      </div>
    </article>
  );
}
