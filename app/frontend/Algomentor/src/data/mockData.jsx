// Mock Data for AlgoMentor

export const userProfile = {
  name: "Alex Chen",
  email: "alex@example.com",
  streak: 7,
  totalProblems: 45,
  level: "Intermediate",
  joinedDate: "2024-01-15"
};

export const skillProgress = [
  { name: "Arrays", progress: 75, problems: 20 },
  { name: "Graphs", progress: 45, problems: 12 },
  { name: "Dynamic Programming", progress: 30, problems: 8 },
  { name: "Trees", progress: 60, problems: 15 },
  { name: "Sorting", progress: 85, problems: 18 },
  { name: "Strings", progress: 55, problems: 14 },
];

export const recentActivity = [
  { problem: "Two Sum", difficulty: "Easy", status: "Completed", date: "2 hours ago" },
  { problem: "Binary Tree Level Order", difficulty: "Medium", status: "In Progress", date: "5 hours ago" },
  { problem: "Longest Palindrome", difficulty: "Medium", status: "Completed", date: "Yesterday" },
];

export const recommendedProblems = [
  {
    id: 1,
    title: "Valid Parentheses",
    difficulty: "Easy",
    tags: ["Stack", "String"],
    acceptance: 89,
    reasoning: "Based on your recent progress in Stack problems"
  },
  {
    id: 2,
    title: "Course Schedule",
    difficulty: "Medium",
    tags: ["Graph", "DFS", "BFS"],
    acceptance: 56,
    reasoning: "Challenge yourself with graph traversal"
  },
  {
    id: 3,
    title: "Coin Change",
    difficulty: "Medium",
    tags: ["Dynamic Programming"],
    acceptance: 52,
    reasoning: "Strengthen your DP foundation"
  },
];

export const problemDetails = {
  id: 1,
  title: "Two Sum",
  difficulty: "Easy",
  tags: ["Array", "Hash Table"],
  description: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nYou can return the answer in any order.",
  constraints: [
    "2 <= nums.length <= 10⁴",
    "-10⁹ <= nums[i] <= 10⁹",
    "-10⁹ <= target <= 10⁹",
    "Only one valid answer exists."
  ],
  examples: [
    {
      input: "nums = [2,7,11,15], target = 9",
      output: "[0,1]",
      explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]."
    },
    {
      input: "nums = [3,2,4], target = 6",
      output: "[1,2]",
      explanation: "Because nums[1] + nums[2] == 6, we return [1, 2]."
    }
  ]
};

export const cognitivePrompts = [
  "What is the input format?",
  "What are the key constraints?",
  "What's the brute force approach?",
  "Can we optimize using a data structure?",
  "What's the time complexity?",
  "What's the space complexity?",
  "Are there edge cases to consider?"
];

export const aiHints = [
  {
    level: 1,
    hint: "Think about how you would solve this manually. What information would you need to keep track of?",
    unlocked: false
  },
  {
    level: 2,
    hint: "Consider using a hash table to store values you've seen. This can help you find complements in O(1) time.",
    unlocked: false
  },
  {
    level: 3,
    hint: "As you iterate through the array, check if (target - current number) exists in your hash table. If yes, you found the pair!",
    unlocked: false
  }
];

export const mockFeedback = {
  understanding: {
    score: 8,
    feedback: "You demonstrated a strong understanding of the problem requirements and constraints."
  },
  approach: {
    score: 7,
    feedback: "Your approach using a hash table is optimal. However, you could improve by explaining the time-space tradeoff more clearly."
  },
  implementation: {
    score: 9,
    feedback: "Clean code with good variable naming. Consider adding comments for complex logic."
  },
  complexity: {
    score: 8,
    feedback: "Correct time complexity analysis (O(n)). Great job identifying the space complexity trade-off."
  },
  mistakes: [
    "Initially missed the edge case where array length is exactly 2",
    "First approach had unnecessary nested loops"
  ],
  strengths: [
    "Quick to recognize the hash table optimization",
    "Clear explanation of the algorithm steps",
    "Good understanding of time complexity"
  ],
  nextSteps: [
    "Practice more hash table problems",
    "Try 'Three Sum' problem next",
    "Review space complexity optimization techniques"
  ]
};