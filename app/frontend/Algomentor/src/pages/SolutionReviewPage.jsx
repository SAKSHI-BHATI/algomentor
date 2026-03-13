import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, AlertCircle, CheckCircle2, Sparkles, ArrowRight } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import ProgressBar from '../components/ProgressBar';
import Badge from '../components/Badge';
import { mockFeedback } from '../data/mockData';

const SolutionReviewPage = () => {
  const navigate = useNavigate();

  const ScoreCard = ({ title, score, feedback, delay }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Card className="p-5" hoverable>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-900">{title}</h3>
          <span className="text-2xl font-bold text-indigo-600">{score}/10</span>
        </div>
        <ProgressBar value={score * 10} showPercentage={false} className="mb-3" />
        <p className="text-sm text-slate-600">{feedback}</p>
      </Card>
    </motion.div>
  );

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center">
            <CheckCircle2 className="w-7 h-7 text-green-600" strokeWidth={1.5} />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-slate-900" data-testid="review-title">
              Solution Review
            </h1>
          </div>
        </div>
        <p className="text-lg text-slate-600 mb-8">Here's your detailed performance analysis</p>
      </motion.div>

      {/* Overall Score */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-8 mb-8 text-center bg-gradient-to-br from-indigo-50 to-violet-50" data-testid="overall-score-card">
          <h2 className="text-lg font-semibold text-slate-700 mb-2">Overall Performance</h2>
          <div className="text-6xl font-bold text-indigo-600 mb-2">8.0</div>
          <p className="text-slate-600">Great job! You're on the right track</p>
        </Card>
      </motion.div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <ScoreCard
          title="Problem Understanding"
          score={mockFeedback.understanding.score}
          feedback={mockFeedback.understanding.feedback}
          delay={0.2}
        />
        <ScoreCard
          title="Approach & Strategy"
          score={mockFeedback.approach.score}
          feedback={mockFeedback.approach.feedback}
          delay={0.3}
        />
        <ScoreCard
          title="Implementation"
          score={mockFeedback.implementation.score}
          feedback={mockFeedback.implementation.feedback}
          delay={0.4}
        />
        <ScoreCard
          title="Complexity Analysis"
          score={mockFeedback.complexity.score}
          feedback={mockFeedback.complexity.feedback}
          delay={0.5}
        />
      </div>

      {/* Mistakes Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mb-8"
      >
        <Card className="p-6" data-testid="mistakes-section">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-amber-600" strokeWidth={1.5} />
            <h2 className="text-xl font-bold text-slate-900">Areas for Improvement</h2>
          </div>
          <ul className="space-y-3">
            {mockFeedback.mistakes.map((mistake, index) => (
              <li key={index} className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <span className="text-amber-600 font-bold mt-0.5">•</span>
                <span className="text-sm text-amber-900">{mistake}</span>
              </li>
            ))}
          </ul>
        </Card>
      </motion.div>

      {/* Strengths Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="mb-8"
      >
        <Card className="p-6" data-testid="strengths-section">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-green-600" strokeWidth={1.5} />
            <h2 className="text-xl font-bold text-slate-900">Your Strengths</h2>
          </div>
          <ul className="space-y-3">
            {mockFeedback.strengths.map((strength, index) => (
              <li key={index} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" strokeWidth={1.5} />
                <span className="text-sm text-green-900">{strength}</span>
              </li>
            ))}
          </ul>
        </Card>
      </motion.div>

      {/* Next Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <Card className="p-6" data-testid="next-steps-section">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-indigo-600" strokeWidth={1.5} />
            <h2 className="text-xl font-bold text-slate-900">Recommended Next Steps</h2>
          </div>
          <div className="space-y-3 mb-6">
            {mockFeedback.nextSteps.map((step, index) => (
              <div key={index} className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-indigo-200 transition-colors cursor-pointer group">
                <div className="w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-bold text-sm">
                  {index + 1}
                </div>
                <span className="text-sm text-slate-700 group-hover:text-indigo-600 transition-colors">{step}</span>
                <ArrowRight className="w-4 h-4 ml-auto text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" strokeWidth={1.5} />
              </div>
            ))}
          </div>

          <div className="flex gap-4">
            <Button onClick={() => navigate('/dashboard')} data-testid="back-dashboard-button">
              Back to Dashboard
            </Button>
            <Button variant="outline" onClick={() => navigate('/problem/2')} data-testid="next-problem-button">
              Try Next Problem
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default SolutionReviewPage;