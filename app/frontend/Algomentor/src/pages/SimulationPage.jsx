import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RotateCcw, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';

const SimulationPage = () => {
  const navigate = useNavigate();
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [showOptimal, setShowOptimal] = useState(false);
  const [userAlgorithm, setUserAlgorithm] = useState(
    `// Your pseudocode from whiteboard\nfunction twoSum(nums, target) {\n  for i from 0 to length-1:\n    for j from i+1 to length:\n      if nums[i] + nums[j] == target:\n        return [i, j]\n}`
  );

  // Mock simulation steps
  const simulationSteps = [
    { step: 1, description: 'Initialize: nums = [2, 7, 11, 15], target = 9', variables: { i: 0, j: 1, nums: [2, 7, 11, 15] } },
    { step: 2, description: 'Check: nums[0] + nums[1] = 2 + 7 = 9', variables: { i: 0, j: 1, sum: 9 } },
    { step: 3, description: 'Match found! Return [0, 1]', variables: { result: [0, 1] } },
  ];

  const optimalAlgorithm = `// Optimal Solution (Hash Table)\nfunction twoSum(nums, target) {\n  map = new HashMap()\n  for i from 0 to length-1:\n    complement = target - nums[i]\n    if complement in map:\n      return [map[complement], i]\n    map[nums[i]] = i\n}`;

  const handleSimulate = () => {
    setIsSimulating(true);
    setCurrentStep(0);
    // Simulate step-by-step
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= simulationSteps.length - 1) {
          clearInterval(interval);
          setIsSimulating(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1500);
  };

  const handleReset = () => {
    setCurrentStep(0);
    setIsSimulating(false);
  };

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
        {/* Left Panel - User Algorithm */}
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
                disabled={isSimulating}
                data-testid="simulate-button"
              >
                {isSimulating ? (
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
          </Card>
        </motion.div>

        {/* Right Panel - Visual Execution */}
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

                {/* Visual Array Representation */}
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
              </div>
            )}
          </Card>
        </motion.div>
      </div>

      {/* Compare with Optimal Solution */}
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
              onClick={() => setShowOptimal(!showOptimal)}
              data-testid="toggle-optimal-button"
            >
              {showOptimal ? 'Hide' : 'Show'} Optimal
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
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Your Approach</h3>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-sm font-mono text-slate-700 mb-2">Time: O(n²)</p>
                    <p className="text-sm font-mono text-slate-700">Space: O(1)</p>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Optimal Approach</h3>
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-sm font-mono text-green-700 mb-2">Time: O(n)</p>
                    <p className="text-sm font-mono text-green-700">Space: O(n)</p>
                  </div>
                </div>

                <div className="md:col-span-2">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Optimal Code</h3>
                  <pre className="p-4 bg-slate-900 text-green-400 rounded-lg font-mono text-sm overflow-x-auto" data-testid="optimal-code">
                    {optimalAlgorithm}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-6 flex justify-end">
            <Button 
              onClick={() => navigate('/solution-review')}
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