import React, { useState, useEffect } from "react";
import { useNewsFeed } from "../../hooks/useNewsFeed";
import NewsFeed from "../NewsFeed";
import Filters from "../Filters";
import api from "../../services/api";

export default function Dashboard() {
  const { news, loading, error, pagination, lastUpdate, applyFilters, refresh } = useNewsFeed();
  const [sources, setSources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [summary, setSummary] = useState({ total: 0, high: 0, medium: 0, low: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sourcesRes, categoriesRes] = await Promise.all([
          api.get("/api/sources/"),
          api.get("/api/categories/"),
        ]);
        setSources(sourcesRes.data);
        setCategories(categoriesRes.data);
      } catch (err) {
        console.error("Failed to fetch sources/categories:", err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    // Compute summary from loaded news
    setSummary({
      total: news.length,
      high: news.filter((n) => n.significance_level === "HIGH").length,
      medium: news.filter((n) => n.significance_level === "MEDIUM").length,
      low: news.filter((n) => n.significance_level === "LOW").length,
    });
  }, [news]);

  const formatLastUpdate = (date) => {
    if (!date) return "—";
    return date.toLocaleTimeString("ru-RU");
  };

  return (
    <div className="dashboard">
      <Filters
        sources={sources}
        categories={categories}
        onApply={applyFilters}
      />

      <div className="news-section">
        <div className="news-header">
          <h2>Лента новостей</h2>
          <div className="news-meta">
            <span className="last-update">
              Обновлено: {formatLastUpdate(lastUpdate)}
            </span>
            <button className="btn-refresh" onClick={refresh}>
              🔄 Обновить сейчас
            </button>
          </div>
        </div>

        <div className="summary-bar">
          <span>📊 Сегодня: {summary.total} новостей</span>
          <span className="summary-high">🔴 {summary.high}</span>
          <span className="summary-medium">🟡 {summary.medium}</span>
          <span className="summary-low">🟢 {summary.low}</span>
        </div>

        <NewsFeed
          news={news}
          loading={loading}
          error={error}
          pagination={pagination}
          onLoadMore={() => {}}
        />
      </div>
    </div>
  );
}
