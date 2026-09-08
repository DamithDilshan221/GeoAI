import React from 'react';

interface CategoryButtonProps {
  label: string;
  code: string;
  isSelected: boolean;
  onClick: () => void;
}

export function CategoryButton({ label, isSelected, onClick }: CategoryButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-6 py-4 text-lg font-medium transition-all ${
        isSelected
          ? 'bg-blue-600 text-white shadow-md shadow-blue-900/50'
          : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
      }`}
    >
      {label}
    </button>
  );
}
