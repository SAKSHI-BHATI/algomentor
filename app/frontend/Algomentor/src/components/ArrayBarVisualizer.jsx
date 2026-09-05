import React from 'react';

const ArrayBarVisualizer = ({ step, stepIndex, totalSteps }) => {
  const values = step?.state || [];
  const max = Math.max(...values.map((value) => Math.abs(Number(value)) || 0), 1);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between text-sm">
        <span className="font-semibold text-slate-800">Array & sorting visualizer</span>
        <span className="text-slate-500">Step {stepIndex + 1} of {totalSteps}</span>
      </div>
      <div className="flex h-52 items-end justify-center gap-2 rounded-xl bg-slate-50 p-4">
        {values.map((value, index) => {
          const active = index === step.idx1 || index === step.idx2;
          const height = `${Math.max(12, (Math.abs(Number(value)) / max) * 100)}%`;
          return (
            <div key={`${index}-${value}`} className="flex h-full min-w-9 flex-1 flex-col justify-end text-center">
              <span className="mb-1 text-xs font-bold text-slate-600">{value}</span>
              <div
                className={`rounded-t-lg transition-all duration-300 ${active ? 'bg-amber-500' : step.is_action ? 'bg-emerald-500' : 'bg-indigo-500'}`}
                style={{ height }}
                title={index === step.idx1 ? 'i' : index === step.idx2 ? 'j' : `index ${index}`}
              />
              <span className={`mt-1 text-xs font-bold ${active ? 'text-amber-700' : 'text-slate-400'}`}>
                {index === step.idx1 && index === step.idx2 ? 'i=j' : index === step.idx1 ? 'i' : index === step.idx2 ? 'j' : index}
              </span>
            </div>
          );
        })}
      </div>
      <p className="mt-4 rounded-lg bg-indigo-50 px-3 py-2 text-sm text-indigo-900">{step?.message}</p>
    </div>
  );
};

export default ArrayBarVisualizer;
