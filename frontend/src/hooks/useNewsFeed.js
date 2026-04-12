import { useState, useEffect, useCallback, useRef } from "react";
import api from "../services/api";

export function useNewsFeed(initialParams = {}) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });
  const [lastUpdate, setLastUpdate] = useState(null);
  const paramsRef = useRef(initialParams);

  const fetchNews = useCallback(async (params = {}) => {
    try {
      setError(null);
      const queryParams = { ...paramsRef.current, ...params, page_size: 20 };
      const response = await api.get("/api/news/", { params: queryParams });
      setNews(response.data.results);
      setPagination({
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
      });
      setLastUpdate(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  // Polling: 30s active, 120s inactive
  useEffect(() => {
    const handleVisibility = () => {
      if (!document.hidden) {
        fetchNews();
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);

    const intervalMs = document.hidden ? 120000 : 30000;
    const interval = setInterval(() => {
      if (!document.hidden) {
        fetchNews();
      }
    }, intervalMs);

    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [fetchNews]);

  const applyFilters = (filters) => {
    paramsRef.current = filters;
    setLoading(true);
    fetchNews(filters);
  };

  return {
    news,
    loading,
    error,
    pagination,
    lastUpdate,
    applyFilters,
    refresh: () => fetchNews(paramsRef.current),
  };
}
