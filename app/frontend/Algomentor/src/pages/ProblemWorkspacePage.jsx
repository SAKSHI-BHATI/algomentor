// ═══════════════════════════════════════════════════════════════════════════
// ProblemWorkspacePage.jsx — ONLY CHANGE: add thinkingState to navigate() call
// Everything else is byte-for-byte identical to the original file.
// ═══════════════════════════════════════════════════════════════════════════
//
// FIND this block (original):
//
//   <Button
//     onClick={() => navigate('/simulation', {
//       state: {problemId,
//         code: whiteboardContent,
//         input: getDefaultInput(problemId)
//       }
//     })}
//   >
//
// REPLACE WITH (one extra line — thinkingState):
//
//   <Button
//     onClick={() => navigate('/simulation', {
//       state: {
//         problemId,
//         code:          whiteboardContent,
//         input:         getDefaultInput(problemId),
//         thinkingState: thinkingState,          // ← ONLY CHANGE
//       }
//     })}
//   >
//
// ═══════════════════════════════════════════════════════════════════════════
// Full file with the change applied:
// ═══════════════════════════════════════════════════════════════════════════

import React, { useState, useEffect } from 'react';
import { useParams,useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Lightbulb, CheckCircle2, Play } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import { problemDetailsMap, cognitivePromptsMap, aiHintsMap } from '../data/mockData';
import UnderstandingModal from '../components/UnderstandingModal';
import { getHint, getNextStep, checkUnderstanding } from '../api';

const ProblemWorkspacePage = () => {
  const navigate = useNavigate();
  const { problemId } = useParams();
  const normalizedProblemId = problemId.replace(/-/g, "_"); // ✅ ADDED
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeMode, setActiveMode] = useState('pseudocode');
  const [whiteboardContent, setWhiteboardContent] = useState('');
  const [showConstraints, setShowConstraints] = useState(true);
  const [showExamples, setShowExamples] = useState(true);
  const [nextStep, setNextStep] = useState('');
  const problemDetails = problemDetailsMap[problemId];
  const [decision, setDecision] = useState("");
  const [feedback, setFeedback] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [hints, setHints] = useState([]);
  const [nextSteps, setNextSteps] = useState([]);
  const [understanding, setUnderstanding] = useState(null);
  const [thinkingState, setThinkingState] = useState("surface_thinking"); // ✅ ADDED

  const getDefaultInput = (problemId) => {
    switch(problemId) {
      case "two-sum":
        return { arr: [2,7,11,15], target: 9 };

      case "valid-parentheses":
        return { s: "()[]{}" };

      case "longest-substring":
        return { s: "abcabcbb" };

      default:
        return {};
    }
  };

  const [showAiFeedback, setShowAiFeedback] = useState(false);

  const modes = [
    { id: 'flowchart', label: 'Create Flowchart', icon: '📊' },
    { id: 'pseudocode', label: 'Write Pseudocode', icon: '📝' },
    { id: 'concept', label: 'Concept Breakdown', icon: '🧠' },
  ];

  useEffect(() => {
    setHints(aiHintsMap[problemId] || []);
  }, [problemId]);

  const fetchNextStep = async () => {
    try {
      const res = await getNextStep(
        normalizedProblemId,              
        whiteboardContent,
        thinkingState,                   
        problemDetails.description       
        );
        setNextStep((res.next_steps || [])[0] || ""); 
    } catch (err) {
      console.error(err);
    }
  };

  const unlockHint = async (index) => {
    try {
      if (!hints.some(h => h.unlocked)) {
        const res = await getHint(
          normalizedProblemId,            
          whiteboardContent,
          thinkingState,                
          problemDetails.description     
          );
        const updatedHints = hints.map((h, i) => ({
          ...h,
          hint: res.hints[i] || "No more hints"
        }));
        updatedHints[index].unlocked = true;
        setHints(updatedHints);
      } else {
        const newHints = [...hints];
        newHints[index].unlocked = true;
        setHints(newHints);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const checkUnderstandingHandler = async () => {
    try {
      const res = await checkUnderstanding(
        whiteboardContent,
        normalizedProblemId,           
        problemDetails.description     
      );
      // ✅ FIXED CHECK
      if (!res.success || !res.result) {
        console.error("Invalid response:", res);
        return;
      }
      const result = res.result;
      setFeedback(result.feedback || "No feedback available");
      setDecision(result.prediction || "unknown"); 
      setThinkingState(result.thinking_state || "surface_thinking"); 
      setShowAiFeedback(true);
    } catch (err) {
      console.error(err);
    }
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
                Didn't understand the problem?
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
                {(cognitivePromptsMap[problemId] || []).map((prompt, index) => (
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
              <Button onClick={fetchNextStep}>
                Next Step
              </Button>
              <Button 
                variant="outline" 
                onClick={checkUnderstandingHandler}
                data-testid="check-understanding-button"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" strokeWidth={1.5} />
                Check Understanding
              </Button>
              {/* ── ONLY CHANGE: thinkingState added to navigate state ────── */}
              <Button 
                onClick={() => navigate('/simulation', {
                  state: {
                    problemId,
                    code:          whiteboardContent,
                    input:         getDefaultInput(problemId),
                    thinkingState: thinkingState,          // ← ONLY CHANGE
                  }
                })}
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
              {showAiFeedback && feedback && (
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
                      <p
                      className={`text-sm font-medium mb-1 ${
                        decision === "optimal"
                        ? "text-green-900"
                        : decision === "better"
                        ? "text-blue-900"
                        : decision === "brute_force"
                        ? "text-yellow-900"
                        : "text-red-900"
                      }`}
                    >
                      {decision === "optimal"
                      ? "Excellent!"
                      : decision === "better"
                      ? "Good attempt!"
                      : decision === "brute_force"
                      ? "Needs optimization"
                      : "Incorrect approach"}
                    </p>
                    <p className="text-sm text-slate-700">{feedback}</p>
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Next Step */}
          {nextStep && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg mt-4">
              <p className="text-sm font-medium text-blue-900 mb-1">Next Step</p>
              <p className="text-sm text-blue-800">{nextStep}</p>
            </div>
          )}
          </div> {/* ✅ closes max-w-4xl */}
        </div> {/* ✅ closes whiteboard area */}
        {/* Understanding Modal */}
        {isModalOpen && (
          <UnderstandingModal
          onClose={() => setIsModalOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

export default ProblemWorkspacePage;
