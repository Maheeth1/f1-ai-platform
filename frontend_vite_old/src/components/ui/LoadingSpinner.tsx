import React from 'react';
import { cn } from '../../utils/cn';

export const LoadingSpinner: React.FC<{ className?: string; size?: 'sm' | 'md' | 'lg' }> = ({ className, size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className={cn('relative inline-block', sizeClasses[size], className)}>
      <div className={cn('absolute inset-0 rounded-full border-f1-border', sizeClasses[size])}></div>
      <div className={cn('absolute inset-0 rounded-full border-t-f1-red animate-spin', sizeClasses[size])}></div>
    </div>
  );
};
