import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Trash2, ArrowRight } from 'lucide-react';
import Button from './Button';

const NODE_TYPES = [
  { type: 'start', label: 'Start / End', color: 'bg-emerald-500 text-white border-emerald-600', shape: 'rounded-full' },
  { type: 'process', label: 'Process / Action', color: 'bg-indigo-600 text-white border-indigo-700', shape: 'rounded-xl' },
  { type: 'decision', label: 'Condition / Decision', color: 'bg-amber-500 text-white border-amber-600', shape: 'rounded-lg rotate-45 sm:rotate-0' },
  { type: 'loop', label: 'Loop (For/While)', color: 'bg-purple-600 text-white border-purple-700', shape: 'rounded-xl' },
  { type: 'io', label: 'Input / Output', color: 'bg-blue-600 text-white border-blue-700', shape: 'rounded-lg -skew-x-6' }
];

const FlowchartCanvas = ({ initialData = [], onChange }) => {
  const [nodes, setNodes] = useState(
    initialData.length > 0 ? initialData : [
      { id: 1, type: 'start', label: 'Start', x: 50, y: 30 },
      { id: 2, type: 'process', label: 'Initialize variables & Hashmap', x: 50, y: 120 },
      { id: 3, type: 'loop', label: 'For each number in array', x: 50, y: 210 },
      { id: 4, type: 'decision', label: 'Is target - num in Hashmap?', x: 50, y: 300 },
      { id: 5, type: 'start', label: 'Return [seen[complement], i]', x: 50, y: 400 },
    ]
  );
  const [selectedNode, setSelectedNode] = useState(null);
  const [newLabel, setNewLabel] = useState('');
  const [selectedType, setSelectedType] = useState('process');

  const addNode = () => {
    if (!newLabel.trim()) return;
    const typeObj = NODE_TYPES.find(t => t.type === selectedType) || NODE_TYPES[1];
    const newNode = {
      id: Date.now(),
      type: selectedType,
      label: newLabel.trim(),
      x: 50,
      y: (nodes.length + 1) * 90
    };
    const updated = [...nodes, newNode];
    setNodes(updated);
    setNewLabel('');
    if (onChange) onChange(updated);
  };

  const removeNode = (id) => {
    const updated = nodes.filter(n => n.id !== id);
    setNodes(updated);
    if (onChange) onChange(updated);
  };

  return (
    <div className="w-full bg-slate-900 rounded-2xl p-6 border border-slate-800 shadow-xl flex flex-col gap-6 text-white">
      {/* Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold flex items-center gap-2">
            <span>📊</span> Interactive Flowchart Builder
          </h3>
          <p className="text-xs text-slate-400">Sketch your logic step-by-step before implementation</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-xs text-slate-200 px-3 py-2 rounded-lg focus:outline-none"
          >
            {NODE_TYPES.map(t => (
              <option key={t.type} value={t.type}>{t.label}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Node description..."
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addNode()}
            className="bg-slate-800 border border-slate-700 text-xs text-slate-200 px-3 py-2 rounded-lg focus:outline-none w-48"
          />
          <Button size="sm" onClick={addNode} className="flex items-center gap-1">
            <Plus className="w-4 h-4" /> Add Node
          </Button>
        </div>
      </div>

      {/* Flowchart Diagram Canvas */}
      <div className="min-h-[420px] bg-slate-950/60 rounded-xl p-8 border border-slate-800/80 flex flex-col items-center gap-4 relative overflow-y-auto">
        {nodes.map((node, index) => {
          const typeInfo = NODE_TYPES.find(t => t.type === node.type) || NODE_TYPES[1];
          return (
            <React.Fragment key={node.id}>
              {/* Node Card */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={`group relative min-w-[220px] max-w-[340px] p-4 text-center border shadow-lg transition-all ${typeInfo.color} ${typeInfo.shape}`}
              >
                <span className="text-sm font-semibold leading-snug block">{node.label}</span>

                {/* Delete overlay button */}
                <button
                  onClick={() => removeNode(node.id)}
                  className="absolute -top-2 -right-2 p-1.5 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity shadow-md hover:bg-red-700"
                  title="Remove node"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </motion.div>

              {/* Connecting Flow Arrow */}
              {index < nodes.length - 1 && (
                <div className="flex flex-col items-center py-1">
                  <div className="w-0.5 h-6 bg-indigo-500/60" />
                  <ArrowRight className="w-4 h-4 text-indigo-400 rotate-90 -mt-1" />
                </div>
              )}
            </React.Fragment>
          );
        })}

        {nodes.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-slate-500 text-sm">
            <p>No nodes added yet.</p>
            <p className="text-xs mt-1">Use the controls above to build your algorithm flowchart.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlowchartCanvas;
