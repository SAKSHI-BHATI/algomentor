import React from 'react';

const DPTableVisualizer = ({ step, stepIndex, totalSteps }) => {
  const values = step?.state || [];
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between text-sm">
        <span className="font-semibold text-slate-800">Dynamic-programming table</span>
        <span className="text-slate-500">Step {stepIndex + 1} of {totalSteps}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 md:grid-cols-6">
        {values.map((value, index) => {
          const active = index === step.idx1;
          return (
            <div key={index} className={`rounded-lg border p-3 text-center transition-colors ${active ? 'border-amber-400 bg-amber-100' : 'border-slate-200 bg-slate-50'}`}>
              <div className="text-xs font-semibold text-slate-500">dp[{index}]</div>
              <div className="mt-1 font-mono text-lg font-bold text-slate-800">{value}</div>
            </div>
          );
        })}
      </div>
      <p className="mt-4 rounded-lg bg-violet-50 px-3 py-2 text-sm text-violet-900">{step?.message}</p>
    </div>
  );
};

export default DPTableVisualizer;
