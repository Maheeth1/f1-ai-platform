import React from 'react';

interface FormSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  icon?: React.ReactNode;
  unit?: string;
}

export const FormSlider: React.FC<FormSliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  onChange,
  icon,
  unit = '',
}) => {
  return (
    <div className="flex flex-col space-y-2 w-full">
      <div className="flex justify-between items-center">
        <span className="flex items-center text-sm font-medium text-gray-400 gap-2">
          {icon && <span className="text-f1-red">{icon}</span>}
          {label}
        </span>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-f1-red/10 text-f1-neon border border-f1-red/20 shadow-[0_0_10px_rgba(225,6,0,0.1)]">
          {value}
          {unit}
        </span>
      </div>
      <div className="relative flex items-center">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-1.5 bg-f1-border rounded-lg appearance-none cursor-pointer accent-f1-red focus:outline-none focus:ring-1 focus:ring-f1-neon transition-all"
        />
      </div>
      <div className="flex justify-between text-[10px] font-mono text-gray-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
};
