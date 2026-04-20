import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RotateCcw, ChevronRight } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { simulateAlgorithm } from '../api';
import { optimalSolutions } from '../data/mockData';

// ─── canvas-confetti (npm install canvas-confetti) ───────────────────────────
// Import is guarded so the app doesn't crash if the package hasn't been
// installed yet — remove the try/catch once you run npm install.
let fireConfetti = null;
try {
  const confettiMod = await import('canvas-confetti').catch(() => null);
  if (confettiMod) fireConfetti = confettiMod.default ?? confettiMod;
} catch (_) { /* package not installed yet */ }

// ─── Completion keywords that trigger balloons (mirrors Streamlit logic) ─────
const COMPLETION_KEYWORDS = [
  "sorted", "complete", "found", "valid", "fibonacci",
  "reversal", "bfs complete", "dfs complete", "execution complete",
];

const isCompletionMessage = (msg) =>
  COMPLETION_KEYWORDS.some((kw) => msg.toLowerCase().includes(kw));

// ─── i/j pointer label colours (mirrors Streamlit render_array_html) ─────────
const POINTER_COLOURS = {
  i:    { color: "#1a7de0" },   // blue
  j:    { color: "#f25c78" },   // red-pink
  ij:   { color: "#f0b429" },   // yellow
};

// ─── Element background colours (mirrors Streamlit CSS classes) ───────────────
const elementStyle = (idx, idx1, idx2, isAction, isDone) => {
  const base = {
    minWidth:      "44px",
    height:        "44px",
    display:       "flex",
    alignItems:    "center",
    justifyContent:"center",
    borderRadius:  "8px",
    fontFamily:    "monospace",
    fontWeight:    700,
    fontSize:      "1rem",
    transition:    "all 0.2s",
    border:        "1px solid rgba(26,111,191,0.2)",
  };

  if (isDone)
    return { ...base, background: "linear-gradient(135deg,#10c97a,#0fa86a)", color: "#fff", transform: "scale(1.08)" };

  const isI   = idx === idx1 && idx !== idx2;
  const isJ   = idx === idx2 && idx !== idx1;
  const isBoth= idx === idx1 && idx === idx2 && idx1 !== -1;

  if (isBoth && isAction)
    return { ...base, background: "linear-gradient(135deg,#f0b429,#f0820f)", color: "#fff", transform: "scale(1.15)" };

  if ((isI || isJ) && isAction)
    return { ...base, background: "linear-gradient(135deg,#f25c78,#d63060)", color: "#fff", transform: "scale(1.18)" };

  if ((isI || isJ) && !isAction)
    return { ...base, background: "linear-gradient(135deg,#f0b429,#f0820f)", color: "#fff", transform: "scale(1.12)" };

  return { ...base, background: "rgba(255,255,255,0.85)", color: "#1a3a5c" };
};

// ─── Pointer label rendered above each array cell ────────────────────────────
const PointerLabel = ({ idx, idx1, idx2 }) => {
  let label = null;
  let style = { fontSize: "0.7rem", fontWeight: 700, fontFamily: "monospace", height: "16px", lineHeight: "16px" };

  if (idx1 !== -1 && idx2 !== -1 && idx === idx1 && idx === idx2) {
    label = "i=j";
    style = { ...style, ...POINTER_COLOURS.ij };
  } else if (idx1 !== -1 && idx === idx1) {
    label = "i";
    style = { ...style, ...POINTER_COLOURS.i };
  } else if (idx2 !== -1 && idx === idx2) {
    label = "j";
    style = { ...style, ...POINTER_COLOURS.j };
  }

  return (
    <div style={{ height: "16px", textAlign: "center" }}>
      {label && <span style={style}>{label}</span>}
    </div>
  );
};

// ─── Array visualisation panel (right panel inner section) ───────────────────
const ArrayVisualization = ({ step, stepIndex, totalSteps }) => {
  if (!step) return null;

  const { state = [], idx1 = -1, idx2 = -1, is_action: isAction = false, message = "" } = step;
  const isDone = isCompletionMessage(message);

  return (
    <div style={{ marginTop: "8px" }}>
      {/* Step counter */}
      <p className="text-sm font-medium text-indigo-900 mb-2">
        Step {stepIndex + 1} of {totalSteps}
      </p>

      {/* Array cells with pointer labels */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", padding: "12px 0" }}>
        {state.map((val, idx) => (
          <div key={idx} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "2px" }}>
            <PointerLabel idx={idx} idx1={idx1} idx2={idx2} />
            <div style={elementStyle(idx, idx1, idx2, isAction, isDone)}>
              {String(val)}
            </div>
          </div>
        ))}
        {state.length === 0 && (
          <span style={{ color: "#8b949e", fontStyle: "italic", fontSize: "0.85rem" }}>
            (empty state)
          </span>
        )}
      </div>

      {/* Step message */}
      <div style={{
        marginTop: "8px",
        padding: "10px 14px",
        borderRadius: "8px",
        background: isDone ? "rgba(16,201,122,0.08)" : "rgba(26,111,191,0.06)",
        border: `1px solid ${isDone ? "rgba(16,201,122,0.25)" : "rgba(26,111,191,0.15)"}`,
        fontSize: "0.85rem",
        color: isDone ? "#0a6641" : "#2a5a8a",
      }}>
        {message}
      </div>
    </div>
  );
};

// ════════════════════════════════════════════════════════════════════════════════
// SIMULATION PAGE
// ════════════════════════════════════════════════════════════════════════════════

const SimulationPage = () => {
  const navigate  = useNavigate();
  const location  = useLocation();

  // ── Read navigation state passed from ProblemWorkspacePage ──────────────────
  const navState     = location.state || {};
  const navProblemId = navState.problemId   || "";         // e.g. "two-sum"
  const navCode      = navState.code        || "";         // user's pseudocode
  const navInput     = navState.input       || {};         // default input values
  const navThinking  = navState.thinkingState || "surface_thinking";

  // Normalise problemId to snake_case for backend
  const backendProblemId = navProblemId.replace(/-/g, "_");  // "two-sum" → "two_sum"

  // ── Existing state (unchanged names / shapes) ────────────────────────────────
  const [isSimulating,   setIsSimulating]   = useState(false);
  const [currentStep,    setCurrentStep]    = useState(0);
  const [showOptimal,    setShowOptimal]    = useState(false);
  const [userAlgorithm,  setUserAlgorithm]  = useState(
    navCode ||
    `// Your pseudocode from whiteboard\nfunction twoSum(nums, target) {\n  for i from 0 to length-1:\n    for j from i+1 to length:\n      if nums[i] + nums[j] == target:\n        return [i, j]\n}`
  );

  // ── New state for live simulation ────────────────────────────────────────────
  const [simSteps,       setSimSteps]       = useState([]);   // fetched steps
  const [isLoadingSim,   setIsLoadingSim]   = useState(false);
  const [simError,       setSimError]       = useState("");
  const [optimalSteps,   setOptimalSteps]   = useState([]);   // optimal sim steps
  const [optimalStep,    setOptimalStep]    = useState(0);
  const [isRunningOpt,   setIsRunningOpt]   = useState(false);
  const [loadingOptSim,  setLoadingOptSim]  = useState(false);

  const intervalRef   = useRef(null);
  const optIntervalRef = useRef(null);

  // ── Derived: optimal metadata from mockData ───────────────────────────────
  const optimalMeta = optimalSolutions[navProblemId] || null;

  // ── Mock simulation steps kept for fallback (unchanged from original) ────────
  const simulationSteps = [
    { step: 1, description: 'Initialize: nums = [2, 7, 11, 15], target = 9', variables: { i: 0, j: 1, nums: [2, 7, 11, 15] } },
    { step: 2, description: 'Check: nums[0] + nums[1] = 2 + 7 = 9', variables: { i: 0, j: 1, sum: 9 } },
    { step: 3, description: 'Match found! Return [0, 1]', variables: { result: [0, 1] } },
  ];

  const optimalAlgorithm = optimalMeta?.code ||
    `// Optimal Solution (Hash Table)\nfunction twoSum(nums, target) {\n  map = new HashMap()\n  for i from 0 to length-1:\n    complement = target - nums[i]\n    if complement in map:\n      return [map[complement], i]\n    map[nums[i]] = i\n}`;

  // ── Confetti helper ───────────────────────────────────────────────────────────
  const triggerConfetti = useCallback(() => {
    if (fireConfetti) {
      fireConfetti({ particleCount: 150, spread: 80, origin: { y: 0.6 } });
    }
  }, []);

  // ── Step animator (user simulation) ─────────────────────────────────────────
  const runStepAnimation = useCallback((steps) => {
    let idx = 0;
    setCurrentStep(0);
    setIsSimulating(true);

    intervalRef.current = setInterval(() => {
      idx += 1;
      setCurrentStep(idx);

      if (idx >= steps.length - 1) {
        clearInterval(intervalRef.current);
        setIsSimulating(false);
        // Feature 3: balloon on completion
        if (steps[idx] && isCompletionMessage(steps[idx].message || "")) {
          triggerConfetti();
        }
      }
    }, 1000);
  }, [triggerConfetti]);

  // ── Step animator (optimal simulation) ───────────────────────────────────────
  const runOptimalAnimation = useCallback((steps) => {
    let idx = 0;
    setOptimalStep(0);
    setIsRunningOpt(true);

    optIntervalRef.current = setInterval(() => {
      idx += 1;
      setOptimalStep(idx);

      if (idx >= steps.length - 1) {
        clearInterval(optIntervalRef.current);
        setIsRunningOpt(false);
        if (steps[idx] && isCompletionMessage(steps[idx].message || "")) {
          triggerConfetti();
        }
      }
    }, 1000);
  }, [triggerConfetti]);

  // Cleanup on unmount
  useEffect(() => () => {
    clearInterval(intervalRef.current);
    clearInterval(optIntervalRef.current);
  }, []);

  // ── Feature 1: Fetch + animate on "Simulate My Algorithm" ───────────────────
  const handleSimulate = async () => {
    clearInterval(intervalRef.current);
    setSimError("");
    setSimSteps([]);
    setCurrentStep(0);

    // If we have a known problem_id, call the backend
    if (backendProblemId) {
      setIsLoadingSim(true);
      try {
        const res = await simulateAlgorithm(
          backendProblemId,
          userAlgorithm,
          navInput,
          false,
        );
        setIsLoadingSim(false);

        if (!res.success) {
          setSimError(res.error || "Simulation failed.");
          // Fall back to mock step animation
          setIsSimulating(true);
          setCurrentStep(0);
          const iv = setInterval(() => {
            setCurrentStep((prev) => {
              if (prev >= simulationSteps.length - 1) { clearInterval(iv); setIsSimulating(false); return prev; }
              return prev + 1;
            });
          }, 1500);
          intervalRef.current = iv;
          return;
        }

        const steps = res.steps || [];
        setSimSteps(steps);
        if (steps.length > 0) {
          runStepAnimation(steps);
        }
      } catch (err) {
        setIsLoadingSim(false);
        setSimError("Network error — is the backend running?");
        // graceful fallback to mock
        setIsSimulating(true);
        setCurrentStep(0);
        const iv = setInterval(() => {
          setCurrentStep((prev) => {
            if (prev >= simulationSteps.length - 1) { clearInterval(iv); setIsSimulating(false); return prev; }
            return prev + 1;
          });
        }, 1500);
        intervalRef.current = iv;
      }
    } else {
      // No problem_id — original mock behaviour
      setIsSimulating(true);
      setCurrentStep(0);
      const iv = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= simulationSteps.length - 1) { clearInterval(iv); setIsSimulating(false); return prev; }
          return prev + 1;
        });
      }, 1500);
      intervalRef.current = iv;
    }
  };

  const handleReset = () => {
    clearInterval(intervalRef.current);
    clearInterval(optIntervalRef.current);
    setCurrentStep(0);
    setIsSimulating(false);
    setOptimalStep(0);
    setIsRunningOpt(false);
    setSimError("");
  };

  // ── Feature 5: Show Optimal — fetch + animate optimal steps ──────────────────
  const handleToggleOptimal = async () => {
    const next = !showOptimal;
    setShowOptimal(next);

    if (next && optimalSteps.length === 0 && backendProblemId) {
      setLoadingOptSim(true);
      try {
        const res = await simulateAlgorithm(backendProblemId, "", navInput, true);
        setLoadingOptSim(false);
        if (res.success && res.steps?.length > 0) {
          setOptimalSteps(res.steps);
          runOptimalAnimation(res.steps);
        }
      } catch (_) {
        setLoadingOptSim(false);
      }
    } else if (next && optimalSteps.length > 0) {
      // Re-play if already fetched
      runOptimalAnimation(optimalSteps);
    }
  };

  // ── Decide which steps/index to show in the right panel ──────────────────────
  // When showOptimal is active we show the optimal run below the user's run.
  const activeSteps     = simSteps.length > 0 ? simSteps : null;
  const activeStep      = activeSteps ? (activeSteps[currentStep] || null) : null;

  const activeOptSteps  = optimalSteps.length > 0 ? optimalSteps : null;
  const activeOptStep   = activeOptSteps ? (activeOptSteps[optimalStep] || null) : null;

  // ── Fallback: use existing mock when no backend steps available ──────────────
  const useMock = simSteps.length === 0;

  // ════════════════════════════════════════════════════════════════════════════
  // RENDER  — all JSX structure is IDENTICAL to the original SimulationPage.
  // Only the internals of the two panels and the optimal section are filled in.
  // ════════════════════════════════════════════════════════════════════════════
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold text-slate-900 mb-2" data-testid="simulation-title">
          Algorithm Simulation
        </h1>
        <p className="text-lg text-slate-600 mb-8">Watch your algorithm execute step-by-step</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* ── LEFT PANEL — Your Algorithm (structure unchanged) ─────────────── */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="p-6" data-testid="user-algorithm-panel">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Your Algorithm</h2>
            <textarea
              value={userAlgorithm}
              onChange={(e) => setUserAlgorithm(e.target.value)}
              className="w-full h-64 font-mono text-sm text-slate-800 bg-slate-50 rounded-lg p-4 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              data-testid="user-algorithm-textarea"
            />
            <div className="flex gap-3 mt-4">
              <Button
                onClick={handleSimulate}
                disabled={isSimulating || isLoadingSim}
                data-testid="simulate-button"
              >
                {isLoadingSim ? (
                  <>Loading…</>
                ) : isSimulating ? (
                  <><Pause className="w-4 h-4 mr-2" strokeWidth={1.5} />Simulating...</>
                ) : (
                  <><Play className="w-4 h-4 mr-2" strokeWidth={1.5} />Simulate My Algorithm</>
                )}
              </Button>
              <Button
                variant="secondary"
                onClick={handleReset}
                data-testid="reset-button"
              >
                <RotateCcw className="w-4 h-4 mr-2" strokeWidth={1.5} />
                Reset
              </Button>
            </div>

            {/* Error banner — inline, no new component */}
            {simError && (
              <p style={{ marginTop: "8px", fontSize: "0.8rem", color: "#c0334d" }}>
                ⚠ {simError}
              </p>
            )}
          </Card>
        </motion.div>

        {/* ── RIGHT PANEL — Step-by-Step Execution (structure unchanged) ───── */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-6 h-full" data-testid="visualization-panel">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Step-by-Step Execution</h2>

            {currentStep === 0 && !isSimulating ? (
              <div className="flex items-center justify-center h-64 text-slate-400">
                <p>Click "Simulate" to start visualization</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* ── Feature 2: i/j array visualisation ──────────────────── */}
                {activeStep && (
                  <ArrayVisualization
                    step={activeStep}
                    stepIndex={currentStep}
                    totalSteps={activeSteps.length}
                  />
                )}

                {/* ── Fallback: original mock current-step display ─────────── */}
                {useMock && (
                  <>
                    {/* Current Step Info */}
                    <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200" data-testid="current-step-info">
                      <p className="text-sm font-medium text-indigo-900 mb-2">
                        Step {simulationSteps[currentStep]?.step || 1} of {simulationSteps.length}
                      </p>
                      <p className="text-sm text-indigo-800">
                        {simulationSteps[currentStep]?.description}
                      </p>
                    </div>

                    {/* Variable State */}
                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                      <h3 className="text-sm font-semibold text-slate-700 mb-3">Current State</h3>
                      <div className="space-y-2" data-testid="variable-state">
                        {Object.entries(simulationSteps[currentStep]?.variables || {}).map(([key, value]) => (
                          <motion.div
                            key={key}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="flex justify-between items-center p-2 bg-white rounded border border-slate-200"
                          >
                            <span className="font-mono text-sm text-slate-700">{key}:</span>
                            <span className="font-mono text-sm text-indigo-600 font-medium">
                              {JSON.stringify(value)}
                            </span>
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    {/* Visual Array Representation (original mock) */}
                    {simulationSteps[currentStep]?.variables.nums && (
                      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <h3 className="text-sm font-semibold text-slate-700 mb-3">Array Visualization</h3>
                        <div className="flex gap-2 justify-center" data-testid="array-visualization">
                          {simulationSteps[currentStep].variables.nums.map((num, idx) => (
                            <motion.div
                              key={idx}
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              transition={{ delay: idx * 0.1 }}
                              className={`w-16 h-16 flex items-center justify-center rounded-lg font-mono font-bold text-lg ${
                                idx === simulationSteps[currentStep].variables.i ||
                                idx === simulationSteps[currentStep].variables.j
                                  ? 'bg-indigo-600 text-white'
                                  : 'bg-white text-slate-700 border border-slate-200'
                              }`}
                            >
                              {num}
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </Card>
        </motion.div>
      </div>

      {/* ── Compare with Optimal Solution (structure unchanged) ──────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="p-6" data-testid="optimal-solution-section">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-slate-900">Compare with Optimal Solution</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={handleToggleOptimal}
              data-testid="toggle-optimal-button"
              disabled={loadingOptSim}
            >
              {loadingOptSim
                ? "Loading…"
                : showOptimal
                ? "Hide Optimal"
                : "Show Optimal"}
            </Button>
          </div>

          <AnimatePresence>
            {showOptimal && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {/* Your Approach */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Your Approach</h3>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-sm font-mono text-slate-700 mb-2">
                      Time: {optimalMeta?.userTime || "O(n²)"}
                    </p>
                    <p className="text-sm font-mono text-slate-700">
                      Space: {optimalMeta?.userSpace || "O(1)"}
                    </p>
                    {optimalMeta?.userApproach && (
                      <p className="text-sm text-slate-500 mt-1">{optimalMeta.userApproach}</p>
                    )}
                  </div>
                </div>

                {/* Optimal Approach */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Optimal Approach</h3>
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-sm font-mono text-green-700 mb-2">
                      Time: {optimalMeta?.timeComplexity || "O(n)"}
                    </p>
                    <p className="text-sm font-mono text-green-700">
                      Space: {optimalMeta?.spaceComplexity || "O(n)"}
                    </p>
                    {optimalMeta?.approach && (
                      <p className="text-sm text-green-600 mt-1 font-medium">{optimalMeta.approach}</p>
                    )}
                  </div>
                </div>

                {/* ── Feature 5: Optimal simulation step visualisation ─────── */}
                {activeOptStep && (
                  <div className="md:col-span-2">
                    <h3 className="text-sm font-semibold text-slate-700 mb-3">
                      Optimal Execution
                      {isRunningOpt && (
                        <span style={{ marginLeft: "8px", fontSize: "0.72rem", color: "#10c97a" }}>
                          ● running
                        </span>
                      )}
                    </h3>
                    <div style={{
                      padding: "12px 16px",
                      background: "rgba(16,201,122,0.04)",
                      border: "1px solid rgba(16,201,122,0.2)",
                      borderRadius: "10px",
                    }}>
                      <ArrayVisualization
                        step={activeOptStep}
                        stepIndex={optimalStep}
                        totalSteps={activeOptSteps.length}
                      />
                    </div>
                  </div>
                )}

                {/* Explanation */}
                {optimalMeta?.explanation && (
                  <div className="md:col-span-2">
                    <h3 className="text-sm font-semibold text-slate-700 mb-2">Why it works</h3>
                    <p className="text-sm text-slate-600">{optimalMeta.explanation}</p>
                  </div>
                )}

                {/* Optimal Code */}
                <div className="md:col-span-2">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Optimal Code</h3>
                  <pre
                    className="p-4 bg-slate-900 text-green-400 rounded-lg font-mono text-sm overflow-x-auto"
                    data-testid="optimal-code"
                  >
                    {optimalAlgorithm}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-6 flex justify-end">
            <Button
              onClick={() => navigate(`/solution-review`)}
              data-testid="view-review-button"
            >
              View Detailed Review
              <ChevronRight className="w-4 h-4 ml-2" strokeWidth={1.5} />
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default SimulationPage;
