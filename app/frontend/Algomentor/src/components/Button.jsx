import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

const Button = React.forwardRef(({ 
  className, 
  variant = 'primary', 
  size = 'default',
  children, 
  ...props 
}, ref) => {
  const variants = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 border-transparent',
    secondary: 'bg-white text-slate-900 hover:bg-slate-50 border-slate-200',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 border-transparent',
    outline: 'bg-transparent text-indigo-600 hover:bg-indigo-50 border-indigo-200',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    default: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      ref={ref}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        'rounded-full font-medium border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
});

Button.displayName = 'Button';

export default Button;