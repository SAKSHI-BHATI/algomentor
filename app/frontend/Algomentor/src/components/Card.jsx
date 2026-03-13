import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

const Card = React.forwardRef(({ 
  className, 
  children,
  hoverable = false,
  ...props 
}, ref) => {
  return (
    <motion.div
      ref={ref}
      whileHover={hoverable ? { borderColor: 'rgb(199 210 254)' } : {}}
      className={cn(
        'bg-white rounded-xl border border-slate-200 shadow-card transition-colors',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
});

Card.displayName = 'Card';

export default Card;