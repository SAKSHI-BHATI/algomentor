// ProblemsListPage.jsx

import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import { problemsList } from '../data/mockData';
/* ---------------------------------- */
/* Mock Data                          */
/* ---------------------------------- */

const MOCK_PROBLEMS = [
  {
    id: 'two-sum',
    title: 'Two Sum',
    difficulty: 'Easy',
    description:
      'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
    tags: ['Array', 'Hash Table'],
  },
  {
    id: 'valid-parentheses',
    title: 'Valid Parentheses',
    difficulty: 'Easy',
    description:
      'Determine if the input string of brackets is valid using stack-based matching logic.',
    tags: ['Stack', 'String'],
  },
  {
    id: 'longest-substring',
    title: 'Longest Substring Without Repeating Characters',
    difficulty: 'Medium',
    description:
      'Find the length of the longest substring without repeating characters using sliding window optimization.',
    tags: ['Sliding Window', 'Hash Table'],
  },
  {
    id: 'merge-intervals',
    title: 'Merge Intervals',
    difficulty: 'Medium',
    description:
      'Merge all overlapping intervals and return an array of the non-overlapping intervals.',
    tags: ['Sorting', 'Array'],
  },
  {
    id: 'binary-tree-level-order',
    title: 'Binary Tree Level Order Traversal',
    difficulty: 'Medium',
    description:
      'Return the level order traversal of a binary tree’s nodes values using BFS.',
    tags: ['Tree', 'BFS'],
  },
  {
    id: 'word-ladder',
    title: 'Word Ladder',
    difficulty: 'Hard',
    description:
      'Given two words and a dictionary, return the length of the shortest transformation sequence.',
    tags: ['Graph', 'BFS'],
  },
  {
    id: 'median-two-sorted',
    title: 'Median of Two Sorted Arrays',
    difficulty: 'Hard',
    description:
      'Find the median of two sorted arrays in logarithmic time complexity.',
    tags: ['Binary Search', 'Divide & Conquer'],
  },
  {
    id: 'product-of-array',
    title: 'Product of Array Except Self',
    difficulty: 'Medium',
    description:
      'Return an array such that each element is the product of all elements except itself without division.',
    tags: ['Array', 'Prefix Sum'],
  },
];

/* ---------------------------------- */
/* Utility: Debounce Hook             */
/* ---------------------------------- */

const useDebouncedValue = (value, delay = 300) => {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debounced;
};

/* ---------------------------------- */
/* Problem Card Component             */
/* ---------------------------------- */

const ProblemCard = React.memo(({ problem, onSolve }) => {
  const handleClick = useCallback(() => {
    onSolve(problem.id);
  }, [onSolve, problem.id]);
  const difficultyColor = {
    Easy: 'bg-green-100 text-green-700',
    Medium: 'bg-amber-100 text-amber-700',
    Hard: 'bg-rose-100 text-rose-700',
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
        className="p-6 h-full flex flex-col justify-between cursor-pointer transition-shadow duration-300 hover:shadow-xl rounded-2xl"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      >
        <div>
          <div className="flex items-center justify-between mb-4">
            <span
              className={`text-xs font-medium px-3 py-1 rounded-full ${difficultyColor[problem.difficulty]}`}
            >
              {problem.difficulty}
            </span>
          </div>

          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            {problem.title}
          </h3>

          <p className="text-sm text-slate-600 line-clamp-2 mb-4">
            {problem.description}
          </p>

          <div className="flex flex-wrap gap-2">
            {problem.tags.map((tag) => (
              <Badge key={tag}>{tag}</Badge>
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

/* ---------------------------------- */
/* Main Page                          */
/* ---------------------------------- */

const ProblemsListPage = () => {
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [activeDifficulty, setActiveDifficulty] = useState('All');

  const debouncedSearch = useDebouncedValue(searchQuery, 300);

  const filteredProblems = useMemo(() => {
    return problemsList.filter((problem) => {
      
      const matchesDifficulty =
        activeDifficulty === 'All' ||
        problem.difficulty === activeDifficulty;

      const matchesSearch =
        problem.title.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        problem.description
          .toLowerCase()
          .includes(debouncedSearch.toLowerCase());

      return matchesDifficulty && matchesSearch;
    });
  }, [debouncedSearch, activeDifficulty]);
  const handleSolve = useCallback(
  (problemId) => {
    navigate(`/problems/workspace/${problemId}`);
  },
  [navigate]
);

  const difficultyFilters = ['All', 'Easy', 'Medium', 'Hard'];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl font-bold text-slate-900">Problems</h1>
          <span className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full">
            {filteredProblems.length}
          </span>
        </div>
        <p className="text-slate-600 text-sm">
          Build your algorithmic thinking
        </p>
      </div>

      {/* Search + Filters */}
      <div className="mb-8 space-y-6">
        <div className="relative max-w-md">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4"
            strokeWidth={1.5}
          />
          <input
            type="text"
            placeholder="Search problems..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
        </div>

        <div className="flex gap-2">
          {difficultyFilters.map((level) => (
            <button
              key={level}
              onClick={() => setActiveDifficulty(level)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeDifficulty === level
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {filteredProblems.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <p className="text-slate-500 text-sm">
            No problems found. Try adjusting your search or filters.
          </p>
        </motion.div>
      ) : (
        <motion.div
          layout
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredProblems.map((problem) => (
            <ProblemCard
              key={problem.id}
              problem={problem}
              onSolve={handleSolve}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default ProblemsListPage;