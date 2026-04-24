import React from "react";
import { cn } from "../../utils/cn";

const variants = {
  HIGH: "bg-red-100 text-red-700 border-red-200",
  MEDIUM: "bg-yellow-100 text-yellow-700 border-yellow-200",
  LOW: "bg-green-100 text-green-700 border-green-200",
};

const icons = {
  HIGH: "🔴",
  MEDIUM: "🟡",
  LOW: "🟢",
};

export default function Badge({ level }) {
  const variant = variants[level] || variants.LOW;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variant
      )}
      data-testid="significance-badge"
    >
      <span>{icons[level]}</span>
      <span>{level}</span>
    </span>
  );
}
