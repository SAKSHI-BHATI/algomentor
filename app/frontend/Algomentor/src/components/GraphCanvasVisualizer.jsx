import React from 'react';
import { motion } from 'framer-motion';

const DEFAULT_GRAPH_LAYOUT = {
  0: { x: 200, y: 50 },
  1: { x: 100, y: 140 },
  2: { x: 300, y: 140 },
  3: { x: 50,  y: 240 },
  4: { x: 150, y: 240 },
  5: { x: 250, y: 240 },
  6: { x: 350, y: 240 }
};

const GraphCanvasVisualizer = ({ step, stepIndex, totalSteps }) => {
  if (!step) return null;

  const graph = step.graph || { 0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6], 3: [1], 4: [1], 5: [2], 6: [2] };
  const currentNode = step.current_node !== undefined ? step.current_node : -1;
  const visited = new Set(step.visited || []);
  const frontier = step.frontier || [];
  const message = step.message || '';
  const isDone = message.toLowerCase().includes('complete') || message.toLowerCase().includes('found');

  const nodeKeys = Object.keys(graph).map(k => isNaN(k) ? k : Number(k));
  
  // Calculate default node layout positions if not in layout map
  const getPos = (node, idx) => {
    if (DEFAULT_GRAPH_LAYOUT[node]) return DEFAULT_GRAPH_LAYOUT[node];
    const angle = (idx / Math.max(1, nodeKeys.length)) * 2 * Math.PI - Math.PI / 2;
    return {
      x: 200 + 130 * Math.cos(angle),
      y: 160 + 100 * Math.sin(angle)
    };
  };

  // Collect unique undirected edges for drawing SVG lines
  const edges = [];
  const edgeSet = new Set();
  nodeKeys.forEach((u, idx) => {
    const uPos = getPos(u, idx);
    (graph[u] || []).forEach(v => {
      const vKey = isNaN(v) ? v : Number(v);
      const key = [u, vKey].sort().join('-');
      if (!edgeSet.has(key)) {
        edgeSet.add(key);
        const vIdx = nodeKeys.indexOf(vKey);
        const vPos = getPos(vKey, vIdx >= 0 ? vIdx : 0);
        edges.push({ u, v: vKey, x1: uPos.x, y1: uPos.y, x2: vPos.x, y2: vPos.y });
      }
    });
  });

  return (
    <div className="w-full bg-slate-900 rounded-2xl p-6 border border-slate-800 text-white space-y-4">
      {/* Header Counter & Message */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
          Graph Traversal Visualization — Step {stepIndex + 1} of {totalSteps}
        </span>
        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${isDone ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-indigo-500/20 text-indigo-300'}`}>
          {isDone ? 'Traversal Complete' : 'Exploring'}
        </span>
      </div>

      {/* SVG Canvas for Graph Diagram */}
      <div className="relative w-full h-[320px] bg-slate-950/80 rounded-xl border border-slate-800/80 flex items-center justify-center overflow-hidden">
        <svg className="w-full h-full" viewBox="0 0 400 300">
          {/* Render Edges */}
          {edges.map((e, i) => {
            const isEdgeActive = (e.u === currentNode && visited.has(e.v)) || (e.v === currentNode && visited.has(e.u));
            return (
              <line
                key={i}
                x1={e.x1}
                y1={e.y1}
                x2={e.x2}
                y2={e.y2}
                stroke={isEdgeActive ? '#818cf8' : '#334155'}
                strokeWidth={isEdgeActive ? 3 : 2}
                strokeDasharray={isEdgeActive ? 'none' : '4 4'}
              />
            );
          })}

          {/* Render Nodes */}
          {nodeKeys.map((node, idx) => {
            const pos = getPos(node, idx);
            const isCurrent = node === currentNode;
            const isVisited = visited.has(node);
            const isFrontier = frontier.includes(node);

            let fillColor = '#1e293b'; // default slate-800
            let strokeColor = '#475569';
            let textColor = '#cbd5e1';

            if (isDone || (isVisited && !isCurrent)) {
              fillColor = '#059669'; // emerald-600
              strokeColor = '#34d399';
              textColor = '#ffffff';
            }
            if (isFrontier && !isCurrent && !isVisited) {
              fillColor = '#7c3aed'; // purple-600
              strokeColor = '#a78bfa';
              textColor = '#ffffff';
            }
            if (isCurrent) {
              fillColor = '#d97706'; // amber-600
              strokeColor = '#fbbf24';
              textColor = '#ffffff';
            }

            return (
              <g key={node}>
                {isCurrent && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={26}
                    fill="none"
                    stroke="#fbbf24"
                    strokeWidth={2}
                    className="animate-ping opacity-75"
                  />
                )}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={20}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={3}
                  className="transition-all duration-300"
                />
                <text
                  x={pos.x}
                  y={pos.y + 5}
                  textAnchor="middle"
                  fill={textColor}
                  fontSize="14"
                  fontWeight="bold"
                  fontFamily="monospace"
                >
                  {String(node)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Traversal State Legend & Frontier Queue/Stack */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
          <span className="font-semibold text-slate-400 block mb-1">Queue / Stack Frontier:</span>
          <div className="flex gap-1.5 flex-wrap">
            {frontier.map((item, i) => (
              <span key={i} className="px-2.5 py-1 bg-purple-900/60 border border-purple-500/40 text-purple-200 rounded-md font-mono font-bold">
                {String(item)}
              </span>
            ))}
            {frontier.length === 0 && <span className="text-slate-500 italic">(empty)</span>}
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
          <span className="font-semibold text-slate-400 block mb-1">Visited Nodes:</span>
          <div className="flex gap-1.5 flex-wrap">
            {Array.from(visited).map((item, i) => (
              <span key={i} className="px-2.5 py-1 bg-emerald-900/60 border border-emerald-500/40 text-emerald-200 rounded-md font-mono font-bold">
                {String(item)}
              </span>
            ))}
            {visited.size === 0 && <span className="text-slate-500 italic">(none)</span>}
          </div>
        </div>
      </div>

      {/* Step Explanation Banner */}
      <div className={`p-3 rounded-xl border text-sm font-medium ${isDone ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-200' : 'bg-indigo-950/60 border-indigo-500/40 text-indigo-200'}`}>
        {message}
      </div>
    </div>
  );
};

export default GraphCanvasVisualizer;
