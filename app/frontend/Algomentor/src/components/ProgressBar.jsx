import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

const ProgressBar = ({ value = 0, label, className, showPercentage = true }) => {
  return (
    <div className={cn('w-full', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-slate-700">{label}</span>}
          {showPercentage && <span className="text-sm text-slate-500">{value}%</span>}
        </div>
      )}
      <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className="h-full bg-gradient-to-r from-indigo-600 to-violet-600 rounded-full"
        />
      </div>
    </div>
  );
};

export default ProgressBar;