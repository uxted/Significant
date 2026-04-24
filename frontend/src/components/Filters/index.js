import React, { useState } from "react";

const SIGNIFICANCE_OPTIONS = [
  { value: "HIGH", label: "🔴 High" },
  { value: "MEDIUM", label: "🟡 Medium" },
  { value: "LOW", label: "🟢 Low" },
];

export default function Filters({ sources = [], categories = [], onApply }) {
  const safeSources = Array.isArray(sources) ? sources : [];
  const safeCategories = Array.isArray(categories) ? categories : [];

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
    if (significance.length > 0)
      filters.significance__in = significance.join(",");
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

  const inputClass =
    "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";
  const selectClass = inputClass;
  const checkboxLabelClass =
    "flex items-center gap-2 text-sm cursor-pointer select-none";

  return (
    <aside className="rounded-lg border bg-card p-4 shadow-sm h-fit sticky top-20">
      <h3 className="font-semibold text-base mb-4">Фильтры</h3>

      {/* Search */}
      <div className="mb-4">
        <label className="text-sm font-medium leading-none mb-2 block">
          Поиск
        </label>
        <input
          type="text"
          placeholder="Ключевая ставка..."
          className={inputClass}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Date range */}
      <div className="mb-4">
        <label className="text-sm font-medium leading-none mb-2 block">
          Дата
        </label>
        <div className="flex gap-2">
          <input
            type="date"
            className="flex h-9 w-1/2 min-w-0 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
          />
          <input
            type="date"
            className="flex h-9 w-1/2 min-w-0 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
          />
        </div>
      </div>

      {/* Significance */}
      <div className="mb-4">
        <label className="text-sm font-medium leading-none mb-2 block">
          Значимость
        </label>
        <div className="flex flex-col gap-2">
          {SIGNIFICANCE_OPTIONS.map((opt) => (
            <label key={opt.value} className={checkboxLabelClass}>
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-input"
                checked={significance.includes(opt.value)}
                onChange={() => handleSignificanceToggle(opt.value)}
              />
              {opt.label}
            </label>
          ))}
        </div>
      </div>

      {/* Category */}
      <div className="mb-4">
        <label className="text-sm font-medium leading-none mb-2 block">
          Категория
        </label>
        <select
          className={selectClass}
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value="">Все категории</option>
          {safeCategories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {/* Source */}
      <div className="mb-4">
        <label className="text-sm font-medium leading-none mb-2 block">
          Источник
        </label>
        <select
          className={selectClass}
          value={selectedSource}
          onChange={(e) => setSelectedSource(e.target.value)}
        >
          <option value="">Все источники</option>
          {safeSources.map((src) => (
            <option key={src.id} value={src.id}>
              {src.name}
            </option>
          ))}
        </select>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-2">
        <button
          className="flex-1 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
            bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2"
          onClick={handleApply}
        >
          Применить
        </button>
        <button
          className="flex-1 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
            border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
          onClick={handleReset}
        >
          Сбросить
        </button>
      </div>
    </aside>
  );
}
