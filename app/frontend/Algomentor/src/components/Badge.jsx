import React from 'react';
import { cn } from '../lib/utils';
import { getDifficultyColor } from '../utils/helpers';

const Badge = ({ children, variant = 'default', className, ...props }) => {
  const variants = {
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    primary: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    success: 'bg-green-50 text-green-700 border-green-200',
  };

  // If children is a difficulty level, use difficulty colors
  const isDifficulty = ['easy', 'medium', 'hard'].includes(children?.toLowerCase());
  const finalClassName = isDifficulty ? getDifficultyColor(children) : variants[variant];

  return (
    <span
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border',
        finalClassName,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;