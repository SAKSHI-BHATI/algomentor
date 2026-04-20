// ================= DASHBOARD DATA =================

export const userProfile = {
  name: "Alex Chen",
  email: "alex@example.com",
  streak: 7,
  totalProblems: 45,
  level: "Intermediate",
  joinedDate: "2024-01-15"
};
// ================= SOLUTION REVIEW MOCK =================

export const mockFeedback = {
  understanding: {
    score: 8,
    feedback: "You demonstrated a strong understanding of the problem requirements and constraints."
  },
  approach: {
    score: 7,
    feedback: "Your approach is good. Try to optimize further."
  },
  implementation: {
    score: 9,
    feedback: "Clean and readable code."
  },
  complexity: {
    score: 8,
    feedback: "Correct time complexity analysis."
  },
  mistakes: [
    "Initial brute force approach",
    "Missed edge cases"
  ],
  strengths: [
    "Good use of data structures",
    "Clear logic"
  ],
  nextSteps: [
    "Practice more problems",
    "Focus on optimization"
  ]
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
    id: 'valid-parentheses',
    title: "Valid Parentheses",
    difficulty: "Easy",
    tags: ["Stack", "String"],
    acceptance: 89,
    reasoning: "Based on your recent progress"
  },
  {
    id: 'two-sum',
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hash Table"],
    acceptance: 95,
    reasoning: "Great for beginners"
  }
];

// ================= PROBLEM LIST (USED IN LIST PAGE) =================

export const problemsList = [
  {
    id: 'two-sum',
    title: 'Two Sum',
    difficulty: 'Easy',
    tags: ['Array', 'Hash Table'],
    description: 'Find two numbers that add up to target.'
  },
  {
    id: 'valid-parentheses',
    title: 'Valid Parentheses',
    difficulty: 'Easy',
    tags: ['Stack', 'String'],
    description: 'Check if brackets are valid.'
  },
  {
    id: 'longest-substring',
    title: 'Longest Substring Without Repeating Characters',
    difficulty: 'Medium',
    tags: ['Sliding Window'],
    description: 'Find longest substring without repeating characters.'
  }
];

// ================= FULL PROBLEM DETAILS =================

export const problemDetailsMap = {
  "two-sum": {
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hash Table"],
    description:
      "Given an array nums and a target, return indices of two numbers that add up to target.\n\nYou may assume each input has exactly one solution.",
    constraints: [
      "2 <= nums.length <= 10⁴",
      "-10⁹ <= nums[i] <= 10⁹",
      "Only one valid answer exists."
    ],
    examples: [
      {
        input: "nums = [2,7,11,15], target = 9",
        output: "[0,1]",
        explanation: "2 + 7 = 9"
      }
    ]
  },

  "valid-parentheses": {
    title: "Valid Parentheses",
    difficulty: "Easy",
    tags: ["Stack"],
    description:
      "Given a string containing just brackets, determine if it is valid.",
    constraints: [
      "1 <= s.length <= 10⁴"
    ],
    examples: [
      {
        input: 's = "()[]{}"',
        output: "true",
        explanation: "All brackets match correctly."
      }
    ]
  },

  "longest-substring": {
    title: "Longest Substring Without Repeating Characters",
    difficulty: "Medium",
    tags: ["Sliding Window"],
    description:
      "Find the length of the longest substring without repeating characters.",
    constraints: [
      "0 <= s.length <= 10⁵"
    ],
    examples: [
      {
        input: 's = "abcabcbb"',
        output: "3",
        explanation: "The answer is 'abc'"
      }
    ]
  }
};

// ================= PROMPTS =================

export const cognitivePromptsMap = {
  "two-sum": [
    "Can we use a hashmap?",
    "What is complement?",
    "How do we optimize from brute force?"
  ],
  "valid-parentheses": [
    "Which data structure helps track order?",
    "When do we push or pop?",
    "How do we match brackets?"
  ],
  "longest-substring": [
    "Can we use sliding window?",
    "How do we track visited characters?",
    "When do we shrink window?"
  ]
};

// ================= HINT STATE (UI ONLY) =================

export const aiHintsMap = {
  "two-sum": [
    { level: 1, hint: "", unlocked: false },
    { level: 2, hint: "", unlocked: false },
    { level: 3, hint: "", unlocked: false }
  ],
  "valid-parentheses": [
    { level: 1, hint: "", unlocked: false },
    { level: 2, hint: "", unlocked: false },
    { level: 3, hint: "", unlocked: false }
  ],
  "longest-substring": [
    { level: 1, hint: "", unlocked: false },
    { level: 2, hint: "", unlocked: false },
    { level: 3, hint: "", unlocked: false }
  ]
};

// ═══════════════════════════════════════════════════════
// NEW: OPTIMAL SOLUTIONS MAP  (only addition below here)
// ═══════════════════════════════════════════════════════

export const optimalSolutions = {
  "two-sum": {
    approach:   "Single-pass HashMap",
    timeComplexity:  "O(n)",
    spaceComplexity: "O(n)",
    explanation:
      "For each element x, compute its complement (target - x). " +
      "Check if the complement already exists in a hashmap of previously seen values. " +
      "If yes, we found our pair. If no, store x → index and continue. " +
      "This avoids the O(n²) nested loop entirely.",
    code:
`def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []`,
    userApproach:   "Nested loops (brute force)",
    userTime:       "O(n²)",
    userSpace:      "O(1)",
  },

  "valid-parentheses": {
    approach:   "Stack (LIFO matching)",
    timeComplexity:  "O(n)",
    spaceComplexity: "O(n)",
    explanation:
      "Push opening brackets onto a stack. When a closing bracket is encountered, " +
      "pop the top of the stack and verify it is the matching opener. " +
      "The string is valid iff the stack is empty at the end.",
    code:
`def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif not stack or stack[-1] != pairs[ch]:
            return False
        else:
            stack.pop()
    return not stack`,
    userApproach:   "Counter-based (insufficient)",
    userTime:       "O(n)",
    userSpace:      "O(1)",
  },

  "longest-substring": {
    approach:   "Sliding Window + HashMap",
    timeComplexity:  "O(n)",
    spaceComplexity: "O(min(m, n))",
    explanation:
      "Maintain a window [left, right] and a hashmap of character → last index. " +
      "When a duplicate is found inside the window, jump left directly to " +
      "max(left, last_seen[char] + 1), avoiding redundant left-pointer steps. " +
      "Track the maximum window size seen.",
    code:
`def length_of_longest_substring(s):
    left = 0
    char_idx = {}
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_idx and char_idx[ch] >= left:
            left = char_idx[ch] + 1
        char_idx[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len`,
    userApproach:   "O(n²) substring enumeration",
    userTime:       "O(n²)",
    userSpace:      "O(min(m, n))",
  },
};
