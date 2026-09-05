import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  Lightbulb,
  CheckCircle2,
  Play,
  Code,
  Save,
  Compass,
  HelpCircle,
  Terminal,
  FileSearch,
  Zap,
  RotateCcw
} from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import FlowchartCanvas from '../components/FlowchartCanvas';
import ConceptBreakdownEditor from '../components/ConceptBreakdownEditor';
import UnderstandingModal from '../components/UnderstandingModal';
import { problemDetailsMap, cognitivePromptsMap, aiHintsMap } from '../data/mockData';
import {
  getHint,
  getNextStep,
  checkUnderstanding,
  evaluateCode,
  fetchProblemDetails,
  fetchUserProgress,
  saveUserProgress,
  fetchMentorUnderstand,
  fetchMentorPatternHint,
  fetchMentorBridge,
  fetchMentorReview,
  executeSolutionCode
} from '../api';

const PIPELINE_STAGES = [
  { id: 1, name: '1. Understand', icon: '💡' },
  { id: 2, name: '2. Whiteboard', icon: '✏️' },
  { id: 3, name: '3. Pattern', icon: '🔍' },
  { id: 4, name: '4. Plan', icon: '📐' },
  { id: 5, name: '5. Visualize', icon: '📊' },
  { id: 6, name: '6. Code & Run', icon: '💻' },
  { id: 7, name: '7. Review', icon: '🤖' },
  { id: 8, name: '8. Debug', icon: '🐞' },
  { id: 9, name: '9. Reflect', icon: '🪞' },
];

const ProblemWorkspacePage = () => {
  const navigate = useNavigate();
  const { problemId } = useParams();
  const normalizedProblemId = problemId.replace(/-/g, "_");

  const [activeStage, setActiveStage] = useState(2);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeMode, setActiveMode] = useState('pseudocode');
  const [whiteboardContent, setWhiteboardContent] = useState('');
  const [flowchartData, setFlowchartData] = useState([]);
  const [conceptData, setConceptData] = useState({});
  const [showConstraints, setShowConstraints] = useState(true);
  const [showExamples, setShowExamples] = useState(true);
  
  // Problem Details
  const [problemDetails, setProblemDetails] = useState(problemDetailsMap[problemId] || {
    title: problemId.replace(/-/g, ' ').toUpperCase(),
    difficulty: "Medium",
    tags: ["DSA"],
    description: "Solve this algorithmic problem using cognitive whiteboard reasoning.",
    constraints: ["1 <= input.length <= 1000"],
    examples: [{ input: "sample input", output: "sample output", explanation: "Sample case" }],
    starter_code: {}
  });

  // Mentor & AI States
  const [understandData, setUnderstandData] = useState(null);
  const [showUnderstandModal, setShowUnderstandModal] = useState(false);
  
  const [patternData, setPatternData] = useState(null);
  const [showPatternModal, setShowPatternModal] = useState(false);
  
  const [bridgeOptions, setBridgeOptions] = useState([]);
  const [showBridgeModal, setShowBridgeModal] = useState(false);
  const [selectedBridgeOpt, setSelectedBridgeOpt] = useState(null);

  const [executionResult, setExecutionResult] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const [reviewResult, setReviewResult] = useState(null);
  const [showReviewModal, setShowReviewModal] = useState(false);

  const [hints, setHints] = useState([]);
  const [thinkingState, setThinkingState] = useState("surface_thinking");
  const [saveStatus, setSaveStatus] = useState("");

  const modes = [
    { id: 'pseudocode', label: 'Write Code / Pseudocode', icon: '📝' },
    { id: 'flowchart', label: 'Create Flowchart', icon: '📊' },
    { id: 'concept', label: 'Concept Breakdown', icon: '🧠' },
  ];

  // Load problem details & user progress on mount
  useEffect(() => {
    const loadData = async () => {
      const dbRes = await fetchProblemDetails(problemId);
      if (dbRes.success && dbRes.problem) {
        setProblemDetails(dbRes.problem);
        if (dbRes.problem.starter_code && dbRes.problem.starter_code.python) {
          setWhiteboardContent(dbRes.problem.starter_code.python);
        }
      } else if (problemDetailsMap[problemId]) {
        setProblemDetails(problemDetailsMap[problemId]);
      }

      const progRes = await fetchUserProgress(problemId);
      if (progRes.success && progRes.progress) {
        if (progRes.progress.whiteboard_content) setWhiteboardContent(progRes.progress.whiteboard_content);
        if (progRes.progress.flowchart_data?.length) setFlowchartData(progRes.progress.flowchart_data);
        if (progRes.progress.concept_breakdown) setConceptData(progRes.progress.concept_breakdown);
      }
    };

    loadData();
    setHints(aiHintsMap[problemId] || [
      { level: 1, hint: "Break the problem into smallest sub-cases.", unlocked: false },
      { level: 2, hint: "Consider data structures offering O(1) lookup.", unlocked: false },
      { level: 3, hint: "Store previously computed results.", unlocked: false },
      { level: 4, hint: "Iterate through input while maintaining target complement state.", unlocked: false },
      { level: 5, hint: "Use a hashmap: `seen[num] = index` for O(1) matching.", unlocked: false }
    ]);
  }, [problemId]);

  const handleSaveProgress = async (status = "attempted") => {
    setSaveStatus("Saving...");
    const res = await saveUserProgress(problemId, status, whiteboardContent, flowchartData, conceptData);
    if (res.success) {
      setSaveStatus("Saved ✅");
      setTimeout(() => setSaveStatus(""), 3000);
    } else {
      setSaveStatus("Save failed");
    }
  };

  // Stage 1: Mentor Understand
  const handleUnderstandClick = async () => {
    setActiveStage(1);
    const res = await fetchMentorUnderstand(problemId, problemDetails.description, (problemDetails.constraints || []).join(", "));
    if (res.success && res.result) {
      setUnderstandData(res.result);
      setShowUnderstandModal(true);
    }
  };

  // Stage 3: Socratic Pattern Hint
  const handlePatternClick = async () => {
    setActiveStage(3);
    const res = await fetchMentorPatternHint(problemId, whiteboardContent, whiteboardContent);
    if (res.success && res.result) {
      setPatternData(res.result);
      setShowPatternModal(true);
    }
  };

  // Bridge Feature (3 Options: solid, exploratory, risky)
  const handleBridgeClick = async () => {
    const res = await fetchMentorBridge(problemId, whiteboardContent, whiteboardContent);
    if (res.success && res.options) {
      setBridgeOptions(res.options);
      setShowBridgeModal(true);
    }
  };

  // Stage 6: Sandboxed Execution
  const handleExecuteCode = async () => {
    setActiveStage(6);
    setIsExecuting(true);
    const res = await executeSolutionCode(problemId, whiteboardContent, "python");
    setIsExecuting(false);
    setExecutionResult(res);
  };

  // Stage 7: AI Code Review
  const handleReviewCode = async () => {
    setActiveStage(7);
    const res = await fetchMentorReview(problemId, whiteboardContent, "python", executionResult);
    if (res.success && res.result) {
      setReviewResult(res.result);
      setShowReviewModal(true);
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
        const fetched = res.hints || [];
        const updatedHints = hints.map((h, i) => ({
          ...h,
          hint: fetched[i] || h.hint || "Analyze boundaries carefully."
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

  const getDefaultInput = (pid) => {
    if (problemDetails.starter_input && Object.keys(problemDetails.starter_input).length > 0) {
      return problemDetails.starter_input;
    }
    switch (pid) {
      case "two-sum": return { nums: [2, 7, 11, 15], target: 9 };
      case "valid-parentheses": return { s: "()[]{}" };
      case "longest-substring": return { s: "abcabcbb" };
      case "binary-search": return { nums: [1, 3, 5, 7, 9, 11], target: 7 };
      case "bubble-sort": return { arr: [64, 34, 25, 12, 22] };
      case "bfs": return { graph: { 0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6], 3: [1], 4: [1], 5: [2], 6: [2] }, start: 0 };
      default: return { arr: [1, 2, 3, 4, 5] };
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-900 text-slate-100">
      {/* 9-Stage Pipeline Header Bar */}
      <div className="bg-slate-950 border-b border-slate-800 px-6 py-3 flex items-center justify-between overflow-x-auto">
        <div className="flex items-center gap-2">
          <span className="text-xl font-black bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mr-4">
            AlgoMentor
          </span>
          <div className="flex items-center gap-1.5 overflow-x-auto">
            {PIPELINE_STAGES.map((stg) => (
              <button
                key={stg.id}
                onClick={() => setActiveStage(stg.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  activeStage === stg.id
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span>{stg.icon}</span>
                <span>{stg.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {saveStatus && <span className="text-xs font-bold text-emerald-400">{saveStatus}</span>}
          <button
            onClick={() => handleSaveProgress('attempted')}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg font-medium flex items-center gap-1.5 transition"
          >
            <Save className="w-3.5 h-3.5" /> Save
          </button>
        </div>
      </div>

      {/* Main Split Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Problem Details & AI Mentor Controls */}
        <div className="w-2/5 border-r border-slate-800 bg-slate-900 overflow-y-auto p-6 space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {problemDetails.difficulty}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300">
                {problemDetails.category}
              </span>
              {problemDetails.pattern && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Pattern: {problemDetails.pattern}
                </span>
              )}
            </div>
            <h1 className="text-2xl font-extrabold text-white mb-2">{problemDetails.title}</h1>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
              {problemDetails.description}
            </p>
          </div>

          {/* Quick Mentor Action Buttons */}
          <div className="grid grid-cols-2 gap-2.5 pt-2">
            <button
              onClick={handleUnderstandClick}
              className="p-3 bg-gradient-to-r from-blue-900/40 to-indigo-900/40 hover:from-blue-900/60 hover:to-indigo-900/60 border border-blue-500/30 rounded-xl text-left transition text-xs font-semibold text-blue-200 flex items-center gap-2"
            >
              <Lightbulb className="w-4 h-4 text-blue-400" /> 1. Understand Problem
            </button>

            <button
              onClick={handlePatternClick}
              className="p-3 bg-gradient-to-r from-purple-900/40 to-pink-900/40 hover:from-purple-900/60 hover:to-pink-900/60 border border-purple-500/30 rounded-xl text-left transition text-xs font-semibold text-purple-200 flex items-center gap-2"
            >
              <FileSearch className="w-4 h-4 text-purple-400" /> 3. Recognize Pattern
            </button>

            <button
              onClick={handleBridgeClick}
              className="col-span-2 p-3.5 bg-gradient-to-r from-emerald-900/40 via-teal-900/40 to-cyan-900/40 hover:from-emerald-900/60 hover:to-cyan-900/60 border border-emerald-500/40 rounded-xl text-left transition text-sm font-bold text-emerald-200 flex items-center justify-between shadow-lg shadow-emerald-950/50"
            >
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-emerald-400 animate-pulse" />
                <span>🌉 Ask Bridge for 3 Next Steps</span>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/30">
                Solid / Exploratory / Risky
              </span>
            </button>
          </div>

          {/* Examples */}
          <div className="border-t border-slate-800 pt-4">
            <button
              onClick={() => setShowExamples(!showExamples)}
              className="flex items-center justify-between w-full text-sm font-bold text-slate-200 mb-2"
            >
              <span>Examples</span>
              {showExamples ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showExamples && (
              <div className="space-y-2.5">
                {(problemDetails.examples || []).map((ex, idx) => (
                  <div key={idx} className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300">
                    <div><span className="text-indigo-400 font-bold">Input:</span> {ex.input}</div>
                    <div><span className="text-emerald-400 font-bold">Output:</span> {ex.output}</div>
                    {ex.explanation && <div className="text-slate-400 mt-1 font-sans text-[11px]">{ex.explanation}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Constraints */}
          <div className="border-t border-slate-800 pt-4">
            <button
              onClick={() => setShowConstraints(!showConstraints)}
              className="flex items-center justify-between w-full text-sm font-bold text-slate-200 mb-2"
            >
              <span>Constraints</span>
              {showConstraints ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showConstraints && (
              <ul className="space-y-1 text-xs text-slate-400 font-mono">
                {(problemDetails.constraints || []).map((c, i) => (
                  <li key={i}>• {c}</li>
                ))}
              </ul>
            )}
          </div>

          {/* 5-Level Progressive AI Hints */}
          <div className="border-t border-slate-800 pt-4">
            <h3 className="text-sm font-bold text-amber-300 mb-3 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-400" /> 5-Level Progressive Hints
            </h3>
            <div className="space-y-2">
              {hints.map((h, i) => (
                <div key={i}>
                  {h.unlocked ? (
                    <div className="p-3 bg-amber-950/40 border border-amber-500/30 rounded-xl text-xs text-amber-200">
                      <div className="font-bold text-amber-400 mb-1">Level {i + 1} Hint</div>
                      <p>{h.hint}</p>
                    </div>
                  ) : (
                    <button
                      onClick={() => unlockHint(i)}
                      className="w-full p-2.5 bg-slate-950 border border-slate-800 hover:border-amber-500/50 rounded-xl text-xs font-medium text-slate-300 flex items-center justify-between transition"
                    >
                      <span>🔒 Unlock Level {i + 1} Hint</span>
                      <span className="text-amber-400 font-bold">Reveal →</span>
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Workspace & Code Execution Sandbox */}
        <div className="flex-1 flex flex-col bg-slate-950 overflow-hidden">
          {/* Mode Switcher Header */}
          <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
            <div className="flex gap-2">
              {modes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setActiveMode(mode.id)}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 ${
                    activeMode === mode.id
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                  }`}
                >
                  <span>{mode.icon}</span>
                  <span>{mode.label}</span>
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExecuteCode}
                disabled={isExecuting}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow-lg shadow-emerald-900/40"
              >
                <Zap className="w-3.5 h-3.5" />
                {isExecuting ? 'Running...' : 'Run Test Cases'}
              </button>

              <button
                onClick={handleReviewCode}
                className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow-lg shadow-purple-900/40"
              >
                <Code className="w-3.5 h-3.5" /> AI Code Review
              </button>

              <button
                onClick={() => {
                  handleSaveProgress("solved");
                  navigate('/simulation', {
                    state: {
                      problemId,
                      code: whiteboardContent,
                      input: getDefaultInput(problemId),
                      thinkingState: thinkingState,
                    }
                  });
                }}
                className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow-lg shadow-indigo-900/40"
              >
                <Play className="w-3.5 h-3.5" /> Simulate Algorithm
              </button>
            </div>
          </div>

          {/* Main Editor Body */}
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {activeMode === 'pseudocode' && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col h-[400px]">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-indigo-400" /> Solution Code / Pseudocode Editor
                  </span>
                  <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                    Python 3.13 Sandbox
                  </span>
                </div>
                <textarea
                  value={whiteboardContent}
                  onChange={(e) => setWhiteboardContent(e.target.value)}
                  placeholder="# Write your Python solution function here..."
                  className="w-full flex-1 font-mono text-sm text-indigo-100 bg-slate-950 p-4 rounded-xl border border-slate-800 outline-none resize-none focus:border-indigo-500 transition"
                />
              </div>
            )}

            {activeMode === 'flowchart' && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 h-[500px]">
                <FlowchartCanvas initialData={flowchartData} onChange={(d) => setFlowchartData(d)} />
              </div>
            )}

            {activeMode === 'concept' && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                <ConceptBreakdownEditor initialData={conceptData} onChange={(d) => setConceptData(d)} />
              </div>
            )}

            {/* Test Case Execution Output Panel */}
            {executionResult && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-emerald-400" /> Execution Harness Results
                  </h3>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                      executionResult.all_passed
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    }`}
                  >
                    {executionResult.all_passed ? 'Passed All Tests ✅' : 'Some Tests Failed ❌'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block">Tests Passed:</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {executionResult.passed_count} / {executionResult.total_count}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block">Total Runtime:</span>
                    <span className="font-mono font-bold text-indigo-400 text-sm">
                      {executionResult.total_time_ms} ms
                    </span>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block">Execution Status:</span>
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      {executionResult.status}
                    </span>
                  </div>
                </div>

                {executionResult.test_results && executionResult.test_results.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Test Case Details:</h4>
                    {executionResult.test_results.map((tc, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-xl border text-xs font-mono ${
                          tc.passed ? 'bg-emerald-950/20 border-emerald-500/30' : 'bg-rose-950/20 border-rose-500/30'
                        }`}
                      >
                        <div className="flex items-center justify-between font-bold mb-1">
                          <span className={tc.passed ? 'text-emerald-400' : 'text-rose-400'}>
                            Test Case #{tc.test_case} — {tc.passed ? 'PASSED' : 'FAILED'}
                          </span>
                          <span className="text-slate-500 text-[11px]">{tc.runtime_ms} ms</span>
                        </div>
                        <div className="text-slate-300">Input: {JSON.stringify(tc.input)}</div>
                        <div className="text-slate-300">Expected: {JSON.stringify(tc.expected)}</div>
                        <div className="text-slate-300">Actual: {JSON.stringify(tc.actual)}</div>
                        {tc.error && <div className="text-rose-400 font-sans mt-1">Error: {tc.error}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stage 1: Understand Problem Modal */}
      {showUnderstandModal && understandData && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-xl w-full text-slate-100 shadow-2xl space-y-4">
            <h3 className="text-lg font-extrabold text-blue-400 flex items-center gap-2">
              <Lightbulb className="w-5 h-5" /> Stage 1: Problem Breakdown & Intuition
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
              {understandData.simplified_explanation}
            </p>
            <div className="p-4 bg-indigo-950/40 border border-indigo-500/30 rounded-xl text-xs text-indigo-200">
              <div className="font-bold text-indigo-400 mb-1">Real-World Analogy:</div>
              <p>{understandData.real_world_analogy}</p>
            </div>
            {understandData.key_objectives && (
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Key Objectives:</h4>
                <ul className="space-y-1 text-xs text-slate-300">
                  {understandData.key_objectives.map((obj, idx) => (
                    <li key={idx}>• {obj}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setShowUnderstandModal(false)}>Got it!</Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Stage 3: Socratic Pattern Modal */}
      {showPatternModal && patternData && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-xl w-full text-slate-100 shadow-2xl space-y-4">
            <h3 className="text-lg font-extrabold text-purple-400 flex items-center gap-2">
              <FileSearch className="w-5 h-5" /> Stage 3: Socratic Pattern Recognition
            </h3>
            <div className="p-4 bg-purple-950/40 border border-purple-500/30 rounded-xl text-xs text-purple-200">
              <div className="font-bold text-purple-400 mb-1">Suggested Pattern Family:</div>
              <p className="text-sm font-semibold">{patternData.pattern_family}</p>
            </div>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300">
              <div className="font-bold text-slate-400 mb-1">Socratic Mentor Question:</div>
              <p className="text-sm italic">"{patternData.socratic_question}"</p>
            </div>
            <p className="text-xs text-slate-400">{patternData.guided_nudge}</p>
            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setShowPatternModal(false)}>Close</Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Bridge Next-Steps Modal (3 Options: solid, exploratory, risky) */}
      {showBridgeModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl w-full text-slate-100 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-extrabold text-emerald-400 flex items-center gap-2">
                <Compass className="w-5 h-5" /> 🌉 Bridge: Evaluate 3 Next Steps
              </h3>
              <span className="text-[11px] text-slate-400">Evaluate each direction carefully!</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Below are 3 possible algorithmic directions to take. Notice that <strong className="text-emerald-400">not all 3 are guaranteed to lead to a correct solution</strong> — practice evaluating confidence and trade-offs:
            </p>

            <div className="space-y-3">
              {bridgeOptions.map((opt) => (
                <div
                  key={opt.id}
                  onClick={() => setSelectedBridgeOpt(opt)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    selectedBridgeOpt?.id === opt.id
                      ? 'border-emerald-500 bg-emerald-950/40 shadow-lg'
                      : 'border-slate-800 bg-slate-950 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="text-sm font-bold text-white">{opt.title}</h4>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase ${
                        opt.confidence === 'solid'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : opt.confidence === 'exploratory'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}
                    >
                      {opt.confidence}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mb-2">{opt.description}</p>
                  <div className="p-2.5 bg-slate-900 rounded-lg text-[11px] text-slate-400 border border-slate-800">
                    <strong className="text-indigo-300">Mentor Insight:</strong> {opt.mentor_insight}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setShowBridgeModal(false)}>Close Bridge</Button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Stage 7: AI Code Review Modal */}
      {showReviewModal && reviewResult && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-xl w-full text-slate-100 shadow-2xl space-y-4">
            <h3 className="text-lg font-extrabold text-purple-400 flex items-center gap-2">
              <Code className="w-5 h-5" /> Stage 7: AI Code Review
            </h3>
            <p className="text-xs text-purple-200 bg-purple-950/40 p-3 rounded-xl border border-purple-500/30">
              {reviewResult.code_summary}
            </p>

            {reviewResult.identified_flaws?.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Identified Flaws:</h4>
                <ul className="space-y-1 text-xs text-rose-300">
                  {reviewResult.identified_flaws.map((flaw, idx) => (
                    <li key={idx}>• {flaw}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300">
              <div className="font-bold text-slate-400 mb-1">Mentor Explanation:</div>
              <p>{reviewResult.mentor_explanation}</p>
            </div>

            {reviewResult.next_refinement_steps?.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Next Refinement Steps:</h4>
                <ul className="space-y-1 text-xs text-emerald-300">
                  {reviewResult.next_refinement_steps.map((step, idx) => (
                    <li key={idx}>• {step}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setShowReviewModal(false)}>Close</Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ProblemWorkspacePage;
