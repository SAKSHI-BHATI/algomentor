import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronUp, Lightbulb, CheckCircle2, Play } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import { problemDetails, cognitivePrompts, aiHints } from '../data/mockData';
import UnderstandingModal from '../components/UnderstandingModal';


const ProblemWorkspacePage = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeMode, setActiveMode] = useState('pseudocode');
  const [whiteboardContent, setWhiteboardContent] = useState('');
  const [showConstraints, setShowConstraints] = useState(true);
  const [showExamples, setShowExamples] = useState(true);
  const [hints, setHints] = useState(aiHints);
  const [showAiFeedback, setShowAiFeedback] = useState(false);

  const modes = [
    { id: 'flowchart', label: 'Create Flowchart', icon: '📊' },
    { id: 'pseudocode', label: 'Write Pseudocode', icon: '📝' },
    { id: 'concept', label: 'Concept Breakdown', icon: '🧠' },
  ];

  const unlockHint = (index) => {
    const newHints = [...hints];
    newHints[index].unlocked = true;
    setHints(newHints);
  };

  const checkUnderstanding = () => {
    setShowAiFeedback(true);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Panel - Problem Description */}
      <div className="w-2/5 border-r border-slate-200 overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Badge>{problemDetails.difficulty}</Badge>
              {problemDetails.tags.map((tag) => (
                <span key={tag} className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full">
                  {tag}
                </span>
              ))}
            </div>
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-bold text-slate-900">
                {problemDetails.title}
              </h1>
              <Button
              variant="outline"
              onClick={() => setIsModalOpen(true)}
              >
                Didn’t understand the problem?
                </Button>
            </div>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-3">Description</h2>
            <p className="text-slate-700 leading-relaxed whitespace-pre-line" data-testid="problem-description">
              {problemDetails.description}
            </p>
          </div>

          {/* Examples */}
          <div className="mb-6">
            <button
              onClick={() => setShowExamples(!showExamples)}
              className="flex items-center justify-between w-full mb-3 text-lg font-semibold text-slate-900"
              data-testid="toggle-examples"
            >
              <span>Examples</span>
              {showExamples ? <ChevronUp className="w-5 h-5" strokeWidth={1.5} /> : <ChevronDown className="w-5 h-5" strokeWidth={1.5} />}
            </button>
            <AnimatePresence>
              {showExamples && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="space-y-4"
                >
                  {problemDetails.examples.map((example, index) => (
                    <Card key={index} className="p-4 bg-slate-50" data-testid={`example-${index}`}>
                      <p className="text-sm font-mono text-slate-700 mb-2">
                        <strong>Input:</strong> {example.input}
                      </p>
                      <p className="text-sm font-mono text-slate-700 mb-2">
                        <strong>Output:</strong> {example.output}
                      </p>
                      {example.explanation && (
                        <p className="text-sm text-slate-600">
                          <strong>Explanation:</strong> {example.explanation}
                        </p>
                      )}
                    </Card>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Constraints */}
          <div>
            <button
              onClick={() => setShowConstraints(!showConstraints)}
              className="flex items-center justify-between w-full mb-3 text-lg font-semibold text-slate-900"
              data-testid="toggle-constraints"
            >
              <span>Constraints</span>
              {showConstraints ? <ChevronUp className="w-5 h-5" strokeWidth={1.5} /> : <ChevronDown className="w-5 h-5" strokeWidth={1.5} />}
            </button>
            <AnimatePresence>
              {showConstraints && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                >
                  <ul className="space-y-2" data-testid="constraints-list">
                    {problemDetails.constraints.map((constraint, index) => (
                      <li key={index} className="text-sm text-slate-700 flex items-start">
                        <span className="text-indigo-600 mr-2">•</span>
                        <span className="font-mono">{constraint}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Right Panel - Cognitive Whiteboard */}
      <div className="flex-1 flex flex-col bg-slate-50">
        {/* Mode Toggle */}
        <div className="p-6 border-b border-slate-200 bg-white">
          <div className="flex gap-2">
            {modes.map((mode) => (
              <button
                key={mode.id}
                onClick={() => setActiveMode(mode.id)}
                data-testid={`mode-${mode.id}`}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  activeMode === mode.id
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <span className="mr-2">{mode.icon}</span>
                {mode.label}
              </button>
            ))}
          </div>
        </div>

        {/* Whiteboard Area */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            {/* Cognitive Prompts */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <h3 className="text-sm font-semibold text-slate-600 mb-3">Guide your thinking:</h3>
              <div className="grid grid-cols-2 gap-3">
                {cognitivePrompts.map((prompt, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-3 bg-white rounded-lg border border-slate-200 text-sm text-slate-600"
                    data-testid={`prompt-${index}`}
                  >
                    {prompt}
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Main Whiteboard */}
            <Card className="p-6 mb-6" data-testid="whiteboard-area">
              <textarea
                value={whiteboardContent}
                onChange={(e) => setWhiteboardContent(e.target.value)}
                placeholder={`Start ${activeMode === 'pseudocode' ? 'writing your pseudocode' : activeMode === 'flowchart' ? 'sketching your flowchart logic' : 'breaking down the concept'}...\n\nThink through:\n- What data structures would help?\n- What's the step-by-step approach?\n- How can you optimize?`}
                className="w-full h-96 font-mono text-sm text-slate-800 bg-transparent border-none outline-none resize-none"
                data-testid="whiteboard-textarea"
              />
            </Card>

            {/* Action Buttons */}
            <div className="flex gap-4 mb-6">
              <Button 
                variant="outline" 
                onClick={checkUnderstanding}
                data-testid="check-understanding-button"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" strokeWidth={1.5} />
                Check Understanding
              </Button>
              <Button 
                onClick={() => navigate('/simulation')}
                data-testid="simulate-button"
              >
                <Play className="w-4 h-4 mr-2" strokeWidth={1.5} />
                Simulate Algorithm
              </Button>
            </div>

            {/* AI Hints */}
            <Card className="p-6 mb-6" data-testid="hints-section">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-amber-500" strokeWidth={1.5} />
                <h3 className="font-semibold text-slate-900">AI Hints</h3>
              </div>
              <div className="space-y-3">
                {hints.map((hint, index) => (
                  <div key={index} data-testid={`hint-${index}`}>
                    {hint.unlocked ? (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-4 bg-amber-50 rounded-lg border border-amber-200"
                      >
                        <p className="text-sm font-medium text-amber-900 mb-1">Hint {hint.level}</p>
                        <p className="text-sm text-amber-800">{hint.hint}</p>
                      </motion.div>
                    ) : (
                      <button
                        onClick={() => unlockHint(index)}
                        className="w-full p-4 bg-slate-100 rounded-lg border border-slate-200 hover:bg-slate-200 transition-colors text-left"
                        data-testid={`unlock-hint-${index}`}
                      >
                        <p className="text-sm font-medium text-slate-700">🔒 Unlock Hint {hint.level}</p>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </Card>

            {/* AI Feedback */}
            <AnimatePresence>
              {showAiFeedback && (
                <motion.div
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 20, scale: 0.95 }}
                  data-testid="ai-feedback-panel"
                >
                  <Card className="p-6 glass-panel">
                    <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                      <span className="text-xl">🤖</span>
                      AI Feedback
                    </h3>
                    <div className="space-y-3">
                      <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <p className="text-sm font-medium text-green-900 mb-1">Great start!</p>
                        <p className="text-sm text-green-800">
                          Your approach shows good understanding of the problem. Consider optimizing your solution using a hash table for O(1) lookups.
                        </p>
                      </div>
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-sm font-medium text-blue-900 mb-1">Next Step</p>
                        <p className="text-sm text-blue-800">
                          Try implementing your pseudocode and then simulate it to see how it performs with different inputs.
                        </p>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
      {/* Understanding Modal */}
      {isModalOpen && (
        <UnderstandingModal
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </div>
  );
};

export default ProblemWorkspacePage;