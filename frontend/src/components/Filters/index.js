import React, { useState } from "react";

const SIGNIFICANCE_OPTIONS = [
  { value: "HIGH", label: "🔴 High" },
  { value: "MEDIUM", label: "🟡 Medium" },
  { value: "LOW", label: "🟢 Low" },
];

export default function Filters({ sources = [], categories = [], onApply }) {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [significance, setSignificance] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedSource, setSelectedSource] = useState("");
  const [search, setSearch] = useState("");

  const handleSignificanceToggle = (value) => {
    setSignificance((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const handleApply = () => {
    const filters = {};
    if (dateFrom) filters.date_from = dateFrom;
    if (dateTo) filters.date_to = dateTo;
    if (significance.length > 0) filters.significance__in = significance.join(",");
    if (selectedCategory) filters.category = selectedCategory;
    if (selectedSource) filters.source = selectedSource;
    if (search.trim()) filters.search = search.trim();
    onApply(filters);
  };

  const handleReset = () => {
    setDateFrom("");
    setDateTo("");
    setSignificance([]);
    setSelectedCategory("");
    setSelectedSource("");
    setSearch("");
    onApply({});
  };

  return (
    <aside className="filters-panel">
      <h3>Фильтры</h3>

      <div className="filter-group">
        <label>Поиск</label>
        <input
          type="text"
          placeholder="Ключевая ставка..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Дата</label>
        <div className="date-range">
          <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
        </div>
      </div>

      <div className="filter-group">
        <label>Значимость</label>
        <div className="checkbox-group">
          {SIGNIFICANCE_OPTIONS.map((opt) => (
            <label key={opt.value} className="checkbox-label">
              <input
                type="checkbox"
                checked={significance.includes(opt.value)}
                onChange={() => handleSignificanceToggle(opt.value)}
              />
              {opt.label}
            </label>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <label>Категория</label>
        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
          <option value="">Все категории</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Источник</label>
        <select value={selectedSource} onChange={(e) => setSelectedSource(e.target.value)}>
          <option value="">Все источники</option>
          {sources.map((src) => (
            <option key={src.id} value={src.id}>
              {src.name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-actions">
        <button className="btn-apply" onClick={handleApply}>
          Применить
        </button>
        <button className="btn-reset" onClick={handleReset}>
          Сбросить
        </button>
      </div>
    </aside>
  );
}
