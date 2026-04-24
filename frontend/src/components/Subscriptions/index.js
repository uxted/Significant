import React, { useState, useEffect } from "react";
import api from "../../services/api";

export default function Subscriptions() {
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [assetInput, setAssetInput] = useState("");
  const [selectedAssets, setSelectedAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [catRes, subRes] = await Promise.all([
          api.get("/api/categories/"),
          api.get("/api/user/subscriptions/"),
        ]);
        setCategories(catRes.data.results || catRes.data);
        setSelectedCategories(subRes.data.categories || []);
        setSelectedAssets(subRes.data.assets || []);
      } catch {
        console.error("Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put("/api/user/subscriptions/", {
        categories: selectedCategories,
        assets: selectedAssets,
      });
    } catch {
      console.error("Failed to save subscriptions");
    } finally {
      setSaving(false);
    }
  };

  const toggleCategory = (catId) => {
    setSelectedCategories((prev) =>
      prev.includes(catId) ? prev.filter((c) => c !== catId) : [...prev, catId]
    );
  };

  const addAsset = () => {
    const ticker = assetInput.trim().toUpperCase();
    if (ticker && !selectedAssets.includes(ticker)) {
      setSelectedAssets((prev) => [...prev, ticker]);
      setAssetInput("");
    }
  };

  const removeAsset = (ticker) => {
    setSelectedAssets((prev) => prev.filter((t) => t !== ticker));
  };

  if (loading)
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-sm text-muted-foreground">Загрузка...</p>
      </div>
    );

  const inputClass =
    "flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2";

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <h2 className="text-2xl font-bold tracking-tight">Подписки</h2>

      {/* Categories */}
      <div className="rounded-lg border bg-card p-6 shadow-sm space-y-4">
        <h3 className="text-lg font-semibold">Категории</h3>
        <div className="flex flex-col gap-3">
          {categories.map((cat) => (
            <label
              key={cat.id}
              className="flex items-center gap-3 text-sm cursor-pointer select-none"
            >
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-input"
                checked={selectedCategories.includes(cat.id)}
                onChange={() => toggleCategory(cat.id)}
              />
              {cat.name}
            </label>
          ))}
        </div>
      </div>

      {/* Assets */}
      <div className="rounded-lg border bg-card p-6 shadow-sm space-y-4">
        <h3 className="text-lg font-semibold">Компании / Тикеры</h3>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="GAZP, SBER, YNDX..."
            className={inputClass}
            value={assetInput}
            onChange={(e) => setAssetInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addAsset()}
          />
          <button
            onClick={addAsset}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
              bg-secondary text-secondary-foreground hover:bg-secondary/80 h-10 px-4"
          >
            Добавить
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {selectedAssets.map((ticker) => (
            <span
              key={ticker}
              className="inline-flex items-center gap-1 rounded-md bg-purple-50 px-2.5 py-1 text-xs font-semibold text-purple-700"
            >
              {ticker}
              <button
                onClick={() => removeAsset(ticker)}
                className="text-purple-500 hover:text-purple-700 ml-1"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Save */}
      <button
        className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
          bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6"
        onClick={handleSave}
        disabled={saving}
      >
        {saving ? "Сохранение..." : "Сохранить"}
      </button>
    </div>
  );
}
