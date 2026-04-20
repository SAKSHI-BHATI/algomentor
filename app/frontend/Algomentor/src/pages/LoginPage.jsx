import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import { ArrowRight, Brain, Sparkles } from 'lucide-react';

// ADDED START ─────────────────────────────────────────────────────────────────
import StarBackground from '../components/StarBackground';
// ADDED END ───────────────────────────────────────────────────────────────────

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    login(email, password);
    navigate('/dashboard');
  };

  const handleDemoLogin = () => {
    login('demo@algomentor.com', 'demo123');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-700 p-12 flex-col justify-between relative overflow-hidden"
      >
        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-72 h-72 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl" />

        {/* ADDED START ── twinkling star layer behind all content ─────────── */}
        <StarBackground />
        {/* ADDED END ──────────────────────────────────────────────────────── */}

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-xl rounded-2xl flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" strokeWidth={1.5} />
            </div>
            <h1 className="text-3xl font-bold text-white">AlgoMentor</h1>
          </div>

          <h2 className="text-5xl font-bold text-white mb-6 leading-tight">
            Build Algorithmic<br />Thinking, Not Just<br />Solutions
          </h2>

          <p className="text-indigo-100 text-lg leading-relaxed max-w-md">
            An intelligent mentor that guides you through structured reasoning,
            visual simulations, and adaptive feedback.
          </p>
        </div>

        <div className="relative z-10 space-y-4">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-indigo-300 mt-1" strokeWidth={1.5} />
            <div>
              <p className="text-white font-medium">Cognitive Whiteboard</p>
              <p className="text-indigo-200 text-sm">Think before you code</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-indigo-300 mt-1" strokeWidth={1.5} />
            <div>
              <p className="text-white font-medium">Visual Algorithm Simulation</p>
              <p className="text-indigo-200 text-sm">See your logic in action</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Right Panel - Login Form (completely unchanged) */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50"
      >
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden mb-8 text-center">
            <h1 className="text-3xl font-bold text-indigo-600">AlgoMentor</h1>
            <p className="text-slate-500 mt-2">Build Algorithmic Thinking</p>
          </div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <h2 className="text-3xl font-bold text-slate-900 mb-2">Welcome back</h2>
            <p className="text-slate-600 mb-8">Sign in to continue your learning journey</p>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <input
                  id="email" type="email" value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  data-testid="email-input"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="alex@example.com" required
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                <input
                  id="password" type="password" value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  data-testid="password-input"
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="••••••••" required
                />
              </div>

              <Button type="submit" className="w-full group" size="lg" data-testid="login-submit-button">
                <span>Sign In</span>
                <ArrowRight className="w-5 h-5 ml-2 inline group-hover:translate-x-1 transition-transform" strokeWidth={1.5} />
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-slate-50 text-slate-500">Or try a demo</span>
                </div>
              </div>
              <Button variant="secondary" className="w-full mt-6" size="lg"
                onClick={handleDemoLogin} data-testid="demo-login-button">
                Demo Login
              </Button>
            </div>

            <p className="mt-8 text-center text-sm text-slate-500">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
