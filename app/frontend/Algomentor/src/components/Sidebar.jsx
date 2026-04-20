import React from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { Home, BookOpen, FlaskConical, Award, User, LogOut } from 'lucide-react';
import { cn } from '../lib/utils';
import logo from '../assets/logo.png'; // ✅ Added logo import

const Sidebar = ({ onLogout }) => {
  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard', testId: 'nav-dashboard' },
    { icon: BookOpen, label: 'Problems', path: '/problems', testId: 'nav-problems' },
    { icon: FlaskConical, label: 'Simulation', path: '/simulation', testId: 'nav-simulation' },
    { icon: Award, label: 'Progress', path: '/solution-review', testId: 'nav-progress' },
    { icon: User, label: 'Profile', path: '/dashboard', testId: 'nav-profile' },
  ];

  return (
    <motion.div 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="h-screen bg-white border-r border-slate-200 flex flex-col w-full"
    >
      {/* Logo */}
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <img 
            src={logo} 
            alt="AlgoMentor Logo" 
            className="h-8 w-auto object-contain"
          />
          <h1 
            className="text-2xl font-bold text-indigo-600" 
            data-testid="app-logo"
          >
            AlgoMentor
          </h1>
        </div>
        <p className="text-sm text-slate-500 mt-1">
          Build Algorithmic Thinking
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              data-testid={item.testId}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 font-medium'
                    : 'text-slate-600 hover:bg-slate-50'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className="w-5 h-5" strokeWidth={1.5} />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-600"
                    />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-slate-200">
        <button
          onClick={onLogout}
          data-testid="logout-button"
          className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-slate-600 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
        >
          <LogOut className="w-5 h-5" strokeWidth={1.5} />
          <span>Logout</span>
        </button>
      </div>
    </motion.div>
  );
};

export default Sidebar;