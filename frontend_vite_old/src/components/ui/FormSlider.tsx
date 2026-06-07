import React from 'react';
import { cn } from '../../utils/cn';

interface FormSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  icon?: React.ReactNode;
  unit?: string;
  className?: string;
}

export const FormSlider: React.FC<FormSliderProps> = ({
  label,
  value,
  min,
  max,
  onChange,
  icon,
  unit = '',
  className,
}) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className={cn('flex flex-col space-y-3', className)}>
      <div className="flex justify-between items-center">
        <label className="flex items-center text-sm font-medium text-gray-400 gap-2">
          {icon && <span className="text-f1-red">{icon}</span>}
          {label}
        </label>
        <span className="text-sm font-bold text-white font-mono bg-f1-border/50 px-2 py-0.5 rounded">
          {value}{unit}
        </span>
      </div>
      <div className="relative pt-1">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-f1-border rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-f1-red z-10 relative bg-transparent"
          style={{
            background: `linear-gradient(to right, var(--color-f1-red) 0%, var(--color-f1-red) ${percentage}%, var(--color-f1-border) ${percentage}%, var(--color-f1-border) 100%)`
          }}
        />
        {/* Custom slider thumb pseudo-styles are usually handled via tailwind or css, but inline gradient serves as progress fill */}
      </div>
    </div>
  );
};
