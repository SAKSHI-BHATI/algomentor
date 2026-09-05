import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import { fetchProblems } from '../api';

const MOCK_PROBLEMS = [
  { id: 'two-sum', title: 'Two Sum', difficulty: 'Easy', description: 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.', tags: ['Array', 'Hash Table'] },
  { id: 'maximum-subarray', title: 'Maximum Subarray', difficulty: 'Medium', description: 'Find the contiguous subarray with the largest sum using Kadane\'s algorithm.', tags: ['Array', 'Dynamic Programming'] },
  { id: 'valid-parentheses', title: 'Valid Parentheses', difficulty: 'Easy', description: 'Determine if the input string of brackets is valid using stack-based matching logic.', tags: ['Stack', 'String'] },
  { id: 'longest-substring', title: 'Longest Substring Without Repeating Characters', difficulty: 'Medium', description: 'Find length of longest substring without repeating characters using sliding window.', tags: ['Sliding Window', 'Hash Table'] },
  { id: 'binary-search', title: 'Binary Search', difficulty: 'Easy', description: 'Given a sorted array of distinct integers nums and a target value, return target index.', tags: ['Binary Search', 'Array'] },
  { id: 'bubble-sort', title: 'Bubble Sort', difficulty: 'Easy', description: 'Step through array, compare adjacent elements, and swap if out of order.', tags: ['Sorting', 'Array'] },
  { id: 'reverse-linked-list', title: 'Reverse Linked List', difficulty: 'Easy', description: 'Given head of singly linked list, reverse list and return reversed list.', tags: ['Linked List'] },
  { id: 'bfs', title: 'Breadth First Search (BFS)', difficulty: 'Medium', description: 'Traverse graph level-by-level starting from source node using a queue.', tags: ['Graph', 'BFS'] },
  { id: 'dfs', title: 'Depth First Search (DFS)', difficulty: 'Medium', description: 'Explore as far as possible along each branch before backtracking.', tags: ['Graph', 'DFS'] },
  { id: 'fibonacci-dp', title: 'Fibonacci Numbers (DP)', difficulty: 'Easy', description: 'Compute n-th Fibonacci number using DP memoization or bottom-up tabulation.', tags: ['Dynamic Programming'] }
];

const useDebouncedValue = (value, delay = 300) => {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debounced;
};

const ProblemCard = React.memo(({ problem, onSolve }) => {
  const handleClick = useCallback(() => {
    onSolve(problem.id);
  }, [onSolve, problem.id]);

  const difficultyColor = {
    Easy: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    Medium: 'bg-amber-100 text-amber-800 border-amber-200',
    Hard: 'bg-rose-100 text-rose-800 border-rose-200',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
      className="h-full"
    >
      <Card
        onClick={handleClick}
        className="p-6 h-full flex flex-col justify-between cursor-pointer transition-shadow duration-300 hover:shadow-xl rounded-2xl border border-slate-200 bg-white"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      >
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className={`text-xs font-bold px-3 py-1 rounded-full border ${difficultyColor[problem.difficulty] || 'bg-slate-100 text-slate-700'}`}>
              {problem.difficulty}
            </span>
            <span className="text-xs text-slate-400 font-medium">{problem.category || 'DSA'}</span>
          </div>

          <h3 className="text-lg font-bold text-slate-900 mb-2 leading-snug">
            {problem.title}
          </h3>

          <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
            {problem.description}
          </p>

          <div className="flex flex-wrap gap-1.5">
            {(problem.tags || []).map((tag) => (
              <Badge key={tag} className="text-[10px] px-2 py-0.5">{tag}</Badge>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <Button onClick={handleClick} className="w-full">
            Solve Problem
          </Button>
        </div>
      </Card>
    </motion.div>
  );
});

const ProblemsListPage = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState(MOCK_PROBLEMS);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeDifficulty, setActiveDifficulty] = useState('All');

  const debouncedSearch = useDebouncedValue(searchQuery, 300);

  useEffect(() => {
    const loadProblems = async () => {
      const res = await fetchProblems();
      if (res.success && res.problems && res.problems.length > 0) {
        setProblems(res.problems);
      }
    };
    loadProblems();
  }, []);

  const filteredProblems = useMemo(() => {
    return problems.filter((problem) => {
      const matchesDifficulty = activeDifficulty === 'All' || problem.difficulty === activeDifficulty;
      const matchesSearch =
        problem.title.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        problem.description.toLowerCase().includes(debouncedSearch.toLowerCase());

      return matchesDifficulty && matchesSearch;
    });
  }, [problems, debouncedSearch, activeDifficulty]);

  const handleSolve = useCallback(
    (problemId) => {
      navigate(`/problems/workspace/${problemId}`);
    },
    [navigate]
  );

  const difficultyFilters = ['All', 'Easy', 'Medium', 'Hard'];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-slate-900">Problem Database</h1>
          <span className="text-xs font-bold px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full">
            {filteredProblems.length} Available
          </span>
        </div>
        <p className="text-slate-600 text-sm">
          Master canonical Data Structures & Algorithms through interactive cognitive tutoring
        </p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search problems or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex gap-2 w-full sm:w-auto">
          {difficultyFilters.map((level) => (
            <button
              key={level}
              onClick={() => setActiveDifficulty(level)}
              className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${
                activeDifficulty === level
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Problem Grid */}
      {filteredProblems.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
          <p className="text-slate-500 text-sm">No problems found matching your query.</p>
        </div>
      ) : (
        <motion.div layout className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProblems.map((problem) => (
            <ProblemCard key={problem.id} problem={problem} onSolve={handleSolve} />
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default ProblemsListPage;