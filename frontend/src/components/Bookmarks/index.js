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
      } catch (err) {
        console.error("Failed to fetch bookmarks:", err);
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

  if (loading) return <div className="loading-spinner">Загрузка...</div>;

  return (
    <div className="bookmarks-page">
      <h2>Закладки</h2>
      {bookmarks.length === 0 ? (
        <div className="empty-state">
          <p>У вас пока нет закладок.</p>
          <Link to="/">Перейти к ленте</Link>
        </div>
      ) : (
        <div className="bookmarks-list">
          {bookmarks.map((article) => (
            <div key={article.id} className="bookmark-item">
              <NewsCard news={article} />
              <button
                className="btn-remove-bookmark"
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
