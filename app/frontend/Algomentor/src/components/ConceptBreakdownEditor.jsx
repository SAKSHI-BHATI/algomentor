import React, { useState } from 'react';

const ConceptBreakdownEditor = ({ initialData = {}, onChange }) => {
  const [breakdown, setBreakdown] = useState({
    input: initialData.input || '',
    output: initialData.output || '',
    constraints: initialData.constraints || '',
    dataStructure: initialData.dataStructure || '',
    variables: initialData.variables || '',
    approach: initialData.approach || '',
    edgeCases: initialData.edgeCases || '',
    timeComplexity: initialData.timeComplexity || '',
    spaceComplexity: initialData.spaceComplexity || '',
  });

  const handleChange = (field, value) => {
    const updated = { ...breakdown, [field]: value };
    setBreakdown(updated);
    if (onChange) onChange(updated);
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6">
      <div className="border-b border-slate-100 pb-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span>🧠</span> Structured Concept Breakdown
        </h3>
        <p className="text-xs text-slate-500">Deconstruct the problem into core algorithmic elements before writing code.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Input & Output */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Given Input
          </label>
          <input
            type="text"
            value={breakdown.input}
            onChange={(e) => handleChange('input', e.target.value)}
            placeholder="e.g., Array of nums [2,7,11,15], target = 9"
            className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Required Output
          </label>
          <input
            type="text"
            value={breakdown.output}
            onChange={(e) => handleChange('output', e.target.value)}
            placeholder="e.g., Indices array [0, 1]"
            className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        {/* Data Structure & Variables */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Chosen Data Structure(s)
          </label>
          <input
            type="text"
            value={breakdown.dataStructure}
            onChange={(e) => handleChange('dataStructure', e.target.value)}
            placeholder="e.g., HashMap / HashSet / Stack / Queue"
            className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Key Variables & State
          </label>
          <input
            type="text"
            value={breakdown.variables}
            onChange={(e) => handleChange('variables', e.target.value)}
            placeholder="e.g., seen = {}, complement = target - num"
            className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Algorithmic Approach */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
          Algorithmic Approach & Strategy
        </label>
        <textarea
          rows={3}
          value={breakdown.approach}
          onChange={(e) => handleChange('approach', e.target.value)}
          placeholder="Describe your step-by-step strategy (e.g., Single pass iteration storing seen numbers in hashmap to check complement in O(1))..."
          className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        />
      </div>

      {/* Edge Cases & Complexities */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Edge Cases
          </label>
          <input
            type="text"
            value={breakdown.edgeCases}
            onChange={(e) => handleChange('edgeCases', e.target.value)}
            placeholder="e.g., Empty input, negative numbers, duplicates"
            className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Expected Time Complexity
          </label>
          <input
            type="text"
            value={breakdown.timeComplexity}
            onChange={(e) => handleChange('timeComplexity', e.target.value)}
            placeholder="e.g., O(n)"
            className="w-full px-3 py-2 text-sm font-mono bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none text-indigo-700"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Expected Space Complexity
          </label>
          <input
            type="text"
            value={breakdown.spaceComplexity}
            onChange={(e) => handleChange('spaceComplexity', e.target.value)}
            placeholder="e.g., O(n)"
            className="w-full px-3 py-2 text-sm font-mono bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none text-indigo-700"
          />
        </div>
      </div>
    </div>
  );
};

export default ConceptBreakdownEditor;
