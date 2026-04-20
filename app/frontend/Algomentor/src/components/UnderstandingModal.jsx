import React, { useReducer, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Button from './Button';
import { checkUnderstanding } from "../api";

const steps = [
  { activeIndex: 0, map: {}, found: false },
  { activeIndex: 1, map: { 2: 0 }, found: false },
  { activeIndex: 2, map: { 2: 0, 7: 1 }, found: true, match: [2, 7] },
];

const initialState = {
  mode: 'animating',
  step: 0,
  reflection: '',
  score: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'PAUSE':
      return { ...state, mode: 'paused' };
    case 'PLAY':
      return { ...state, mode: 'animating' };
    case 'NEXT':
      return { ...state, step: Math.min(state.step + 1, steps.length - 1) };
    case 'PREV':
      return { ...state, step: Math.max(state.step - 1, 0) };
    case 'COMPLETE':
      return { ...state, mode: 'reflection' };
    case 'SET_REFLECTION':
      return { ...state, reflection: action.payload };
    case 'EVALUATE':
      return { ...state, mode: 'evaluation', score: action.payload };
    case 'REPLAY':
      return { ...initialState };
    default:
      return state;
  }
}

const UnderstandingModal = ({ onClose }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (state.mode === 'animating') {
      intervalRef.current = setInterval(() => {
        dispatch({ type: 'NEXT' });
      }, 1500);
    }
    return () => clearInterval(intervalRef.current);
  }, [state.mode]);

  useEffect(() => {
    if (state.step === steps.length - 1 && state.mode === 'animating') {
      setTimeout(() => dispatch({ type: 'COMPLETE' }), 1200);
    }
  }, [state.step, state.mode]);

  const evaluate = async () => {
    try {
      const text = `Problem: Two Sum | Thought: ${state.reflection}`;
      const res = await checkUnderstanding(text);
      const decision = res.result.decision;   // PROCEED / WATCH
      // Convert to your UI score system
      const score = decision === "PROCEED" ? 2 : 1;
      dispatch({ type: 'EVALUATE', payload: score });
    } catch (err) {
      console.error(err);
    }
  };

  const current = steps[state.step];
  const array = [2, 7, 11];

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/30 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl p-8 z-10"
        >
          {state.mode === 'animating' || state.mode === 'paused' ? (
            <>
              <h3 className="text-xl font-semibold mb-6">
                Visualizing Two Sum
              </h3>

              {/* Array Visualization */}
              <div className="flex gap-4 justify-center mb-8">
                {array.map((num, index) => (
                  <motion.div
                    key={index}
                    layout
                    className={`w-16 h-16 flex items-center justify-center rounded-xl border ${
                      current.activeIndex === index
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-100'
                    }`}
                  >
                    {num}
                  </motion.div>
                ))}
              </div>

              {/* Controls */}
              <div className="flex justify-between items-center">
                <div className="text-sm text-slate-500">
                  Step {state.step + 1} / {steps.length}
                </div>

                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => dispatch({ type: 'PREV' })}>
                    Prev
                  </Button>
                  {state.mode === 'paused' ? (
                    <Button onClick={() => dispatch({ type: 'PLAY' })}>
                      Play
                    </Button>
                  ) : (
                    <Button onClick={() => dispatch({ type: 'PAUSE' })}>
                      Pause
                    </Button>
                  )}
                  <Button onClick={() => dispatch({ type: 'NEXT' })}>
                    Next
                  </Button>
                </div>
              </div>
            </>
          ) : null}

          {state.mode === 'reflection' && (
            <>
              <h3 className="text-lg font-semibold mb-4">
                Explain What You Understood
              </h3>
              <textarea
                value={state.reflection}
                onChange={(e) =>
                  dispatch({
                    type: 'SET_REFLECTION',
                    payload: e.target.value,
                  })
                }
                className="w-full h-40 p-4 border rounded-xl text-sm"
              />
              <div className="flex gap-4 mt-4">
                <Button onClick={evaluate}>Evaluate</Button>
              </div>
            </>
          )}

          {state.mode === 'evaluation' && (
            <>
              {state.score === 2 ? (
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  Strong understanding! Proceed to solve.
                </div>
              ) : (
                <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                  Review the animation again.
                </div>
              )}
              <div className="flex gap-4 mt-4">
                <Button variant="outline" onClick={() => dispatch({ type: 'REPLAY' })}>
                  Replay
                </Button>
                <Button onClick={onClose}>Proceed</Button>
              </div>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default UnderstandingModal;