import React from 'react';

const LinkedListVisualizer = ({ step, stepIndex, totalSteps }) => {
  const state = (step?.state || []).filter((item) => item !== '→');
  const splitAt = (step?.state || []).indexOf('→');

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between text-sm">
        <span className="font-semibold text-slate-800">Linked-list pointer visualizer</span>
        <span className="text-slate-500">Step {stepIndex + 1} of {totalSteps}</span>
      </div>
      <div className="overflow-x-auto rounded-xl bg-slate-50 p-5">
        <div className="flex min-w-max items-center gap-2">
          <span className="mr-2 text-xs font-bold uppercase tracking-wide text-emerald-700">head</span>
          {state.map((value, index) => {
            const isReversed = splitAt >= 0 && index < splitAt;
            return (
              <React.Fragment key={`${index}-${value}`}>
                <div className={`rounded-lg border-2 px-4 py-3 font-mono font-bold ${isReversed ? 'border-emerald-500 bg-emerald-50 text-emerald-800' : 'border-indigo-500 bg-indigo-50 text-indigo-800'}`}>
                  {value}
                </div>
                {index < state.length - 1 && <span className="text-xl font-bold text-slate-400">→</span>}
              </React.Fragment>
            );
          })}
          {!state.length && <span className="text-slate-500">empty list</span>}
          <span className="ml-2 text-xs font-bold uppercase tracking-wide text-slate-500">null</span>
        </div>
      </div>
      <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">{step?.message}</p>
    </div>
  );
};

export default LinkedListVisualizer;
