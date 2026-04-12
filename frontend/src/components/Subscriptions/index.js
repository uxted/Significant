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
        setCategories(catRes.data);
        setSelectedCategories(subRes.data.categories || []);
        setSelectedAssets(subRes.data.assets || []);
      } catch (err) {
        console.error("Failed to fetch data:", err);
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
    } catch (err) {
      console.error("Failed to save subscriptions:", err);
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

  if (loading) return <div className="loading-spinner">Загрузка...</div>;

  return (
    <div className="subscriptions-page">
      <h2>Подписки</h2>

      <div className="subscription-section">
        <h3>Категории</h3>
        <div className="category-list">
          {categories.map((cat) => (
            <label key={cat.id} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedCategories.includes(cat.id)}
                onChange={() => toggleCategory(cat.id)}
              />
              {cat.name}
            </label>
          ))}
        </div>
      </div>

      <div className="subscription-section">
        <h3>Компании / Тикеры</h3>
        <div className="asset-input">
          <input
            type="text"
            placeholder="GAZP, SBER, YNDX..."
            value={assetInput}
            onChange={(e) => setAssetInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addAsset()}
          />
          <button onClick={addAsset}>Добавить</button>
        </div>
        <div className="asset-tags">
          {selectedAssets.map((ticker) => (
            <span key={ticker} className="asset-ticker-tag">
              {ticker}
              <button onClick={() => removeAsset(ticker)}>×</button>
            </span>
          ))}
        </div>
      </div>

      <button className="btn-save" onClick={handleSave} disabled={saving}>
        {saving ? "Сохранение..." : "Сохранить"}
      </button>
    </div>
  );
}
