import React, { useState, useEffect } from "react";
import { useNewsFeed } from "../../hooks/useNewsFeed";
import NewsFeed from "../NewsFeed";
import Filters from "../Filters";
import api from "../../services/api";

export default function Dashboard() {
  const { news, loading, error, pagination, lastUpdate, applyFilters, refresh } =
    useNewsFeed();
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
        setSources(sourcesRes.data.results || sourcesRes.data);
        setCategories(categoriesRes.data.results || categoriesRes.data);
      } catch (err) {
        console.error("Failed to fetch sources/categories:", err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
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
    <div className="container py-6">
      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-80 flex-shrink-0">
          <Filters
            sources={sources}
            categories={categories}
            onApply={applyFilters}
          />
        </div>

        {/* Main content */}
        <div className="flex-1 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold tracking-tight">Лента новостей</h2>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground">
                Обновлено: {formatLastUpdate(lastUpdate)}
              </span>
              <button
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
                  border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
                onClick={refresh}
              >
                🔄 Обновить
              </button>
            </div>
          </div>

          {/* Summary */}
          <div className="flex gap-4 rounded-lg border bg-card p-4 shadow-sm">
            <span className="text-sm font-medium">
              📊 Сегодня: {summary.total} новостей
            </span>
            <span className="text-sm font-semibold text-red-600">
              🔴 {summary.high}
            </span>
            <span className="text-sm font-semibold text-yellow-600">
              🟡 {summary.medium}
            </span>
            <span className="text-sm font-semibold text-green-600">
              🟢 {summary.low}
            </span>
          </div>

          {/* Feed */}
          <NewsFeed
            news={news}
            loading={loading}
            error={error}
            pagination={pagination}
            onLoadMore={() => {}}
          />
        </div>
      </div>
    </div>
  );
}
