import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../services/api";
import NewsCard from "../NewsCard";

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBookmarks = async () => {
      try {
        const response = await api.get("/api/user/bookmarks/");
        setBookmarks(response.data);
      } catch {
        console.error("Failed to fetch bookmarks");
      } finally {
        setLoading(false);
      }
    };
    fetchBookmarks();
  }, []);

  const handleRemove = async (articleId) => {
    await api.delete(`/api/user/bookmarks/${articleId}/`);
    setBookmarks((prev) => prev.filter((b) => b.id !== articleId));
  };

  if (loading)
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-sm text-muted-foreground">Загрузка...</p>
      </div>
    );

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Закладки</h2>
      {bookmarks.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border bg-card p-12 text-center shadow-sm">
          <p className="text-lg font-medium">У вас пока нет закладок.</p>
          <Link to="/" className="mt-4 text-primary underline-offset-4 hover:underline">
            Перейти к ленте
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookmarks.map((article) => (
            <div key={article.id} className="space-y-2">
              <NewsCard news={article} />
              <button
                className="text-sm text-muted-foreground hover:text-destructive transition-colors"
                onClick={() => handleRemove(article.id)}
              >
                Удалить из закладок
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
