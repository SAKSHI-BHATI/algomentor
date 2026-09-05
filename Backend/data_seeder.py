"""
data_seeder.py — Database seeder for AlgoMentor problem database
"""

import json
from Backend.database import init_db, SessionLocal
from Backend.models import Problem, User, StudentKnowledge
from Backend.routes.auth_routes import hash_password

PROBLEMS_DATA = [
    {
        "id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Arrays",
        "pattern": "Hash Table / Two Pointers",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "tags_json": json.dumps(["Array", "Hash Table"]),
        "constraints_json": json.dumps([
            "2 <= nums.length <= 10⁴",
            "-10⁹ <= nums[i] <= 10⁹",
            "-10⁹ <= target <= 10⁹",
            "Only one valid answer exists."
        ]),
        "examples_json": json.dumps([
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": "3 + 2 + 4 -> nums[1] + nums[2] == 6."}
        ]),
        "prompts_json": json.dumps([
            "Can we use a HashMap to store seen complements?",
            "What is complement value target - num?",
            "How do we optimize from O(n²) nested loop to O(n)?"
        ]),
        "starter_input_json": json.dumps({"nums": [2, 7, 11, 15], "target": 9}),
        "starter_code_json": json.dumps({
            "python": "def two_sum(nums, target):\n    # Write your solution here\n    pass",
            "javascript": "function twoSum(nums, target) {\n    // Write your solution here\n}"
        }),
        "entry_function": "two_sum",
        "test_cases_json": json.dumps([
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]}
        ]),
        "solution_code": "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []"
    },
    {
        "id": "maximum-subarray",
        "title": "Maximum Subarray (Kadane's)",
        "difficulty": "Medium",
        "category": "Arrays",
        "pattern": "Dynamic Programming",
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "tags_json": json.dumps(["Array", "Dynamic Programming"]),
        "constraints_json": json.dumps([
            "1 <= nums.length <= 10⁵",
            "-10⁴ <= nums[i] <= 10⁴"
        ]),
        "examples_json": json.dumps([
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum 6."}
        ]),
        "prompts_json": json.dumps([
            "When should we reset current sum?",
            "How does Kadane's algorithm decide whether to extend or start fresh?"
        ]),
        "starter_input_json": json.dumps({"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}),
        "starter_code_json": json.dumps({
            "python": "def max_sub_array(nums):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "max_sub_array",
        "test_cases_json": json.dumps([
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [1]}, "expected": 1},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23}
        ]),
        "solution_code": "def max_sub_array(nums):\n    curr = best = nums[0]\n    for x in nums[1:]:\n        curr = max(x, curr + x)\n        best = max(best, curr)\n    return best"
    },
    {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "category": "Stacks",
        "pattern": "Monotonic / LIFO Stack",
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if open brackets are closed by the same type of brackets and closed in the correct order.",
        "tags_json": json.dumps(["Stack", "String"]),
        "constraints_json": json.dumps([
            "1 <= s.length <= 10⁴",
            "s consists of parentheses only '()[]{}'."
        ]),
        "examples_json": json.dumps([
            {"input": 's = "()[]{}"', "output": "true", "explanation": "All opening brackets are matched correctly in order."}
        ]),
        "prompts_json": json.dumps([
            "Which data structure tracks Last-In First-Out order?",
            "When do we push vs pop?",
            "What condition guarantees valid stack state?"
        ]),
        "starter_input_json": json.dumps({"s": "({[]})"}),
        "starter_code_json": json.dumps({
            "python": "def is_valid(s):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "is_valid",
        "test_cases_json": json.dumps([
            {"input": {"s": "()"}, "expected": True},
            {"input": {"s": "()[]{}"}, "expected": True},
            {"input": {"s": "(]"}, "expected": False}
        ]),
        "solution_code": "def is_valid(s):\n    stack = []\n    pairs = {')': '(', ']': '[', '}': '{'}\n    for ch in s:\n        if ch in '([{': stack.append(ch)\n        elif not stack or stack[-1] != pairs[ch]: return False\n        else: stack.pop()\n    return not stack"
    },
    {
        "id": "longest-substring",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "category": "Strings",
        "pattern": "Sliding Window",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "tags_json": json.dumps(["Sliding Window", "Hash Table", "String"]),
        "constraints_json": json.dumps([
            "0 <= s.length <= 5 * 10⁴",
            "s consists of English letters, digits, symbols and spaces."
        ]),
        "examples_json": json.dumps([
            {"input": 's = "abcabcbb"', "output": "3", "explanation": "The answer is 'abc', with the length of 3."}
        ]),
        "prompts_json": json.dumps([
            "Can we use a sliding window pointer pair (left, right)?",
            "How do we update the left pointer when a duplicate is seen?"
        ]),
        "starter_input_json": json.dumps({"s": "abcabcbb"}),
        "starter_code_json": json.dumps({
            "python": "def length_of_longest_substring(s):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "length_of_longest_substring",
        "test_cases_json": json.dumps([
            {"input": {"s": "abcabcbb"}, "expected": 3},
            {"input": {"s": "bbbbb"}, "expected": 1},
            {"input": {"s": "pwwkew"}, "expected": 3}
        ]),
        "solution_code": "def length_of_longest_substring(s):\n    left = 0\n    seen = {}\n    max_len = 0\n    for right, ch in enumerate(s):\n        if ch in seen and seen[ch] >= left:\n            left = seen[ch] + 1\n        seen[ch] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len"
    },
    {
        "id": "binary-search",
        "title": "Binary Search",
        "difficulty": "Easy",
        "category": "Searching",
        "pattern": "Binary Search",
        "description": "Given a sorted array of distinct integers nums and a target value, return the index if the target is found. Otherwise return -1.",
        "tags_json": json.dumps(["Binary Search", "Array"]),
        "constraints_json": json.dumps([
            "1 <= nums.length <= 10⁴",
            "nums is sorted in ascending order."
        ]),
        "examples_json": json.dumps([
            {"input": "nums = [1,3,5,7,9,11], target = 7", "output": "3", "explanation": "7 exists in nums at index 3."}
        ]),
        "prompts_json": json.dumps([
            "What is the midpoint formula mid = (low + high) // 2?",
            "How do low and high pointers shift based on nums[mid] vs target?"
        ]),
        "starter_input_json": json.dumps({"nums": [1, 3, 5, 7, 9, 11], "target": 7}),
        "starter_code_json": json.dumps({
            "python": "def binary_search(nums, target):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "binary_search",
        "test_cases_json": json.dumps([
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected": 4},
            {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected": -1}
        ]),
        "solution_code": "def binary_search(nums, target):\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target: return mid\n        elif nums[mid] < target: low = mid + 1\n        else: high = mid - 1\n    return -1"
    },
    {
        "id": "bubble-sort",
        "title": "Bubble Sort Visualization",
        "difficulty": "Easy",
        "category": "Sorting",
        "pattern": "Sorting",
        "description": "Repeatedly step through the array, compare adjacent elements and swap them if they are in the wrong order.",
        "tags_json": json.dumps(["Sorting", "Array"]),
        "constraints_json": json.dumps(["1 <= arr.length <= 100"]),
        "examples_json": json.dumps([
            {"input": "arr = [64, 34, 25, 12, 22]", "output": "[12, 22, 25, 34, 64]", "explanation": "Elements sorted in ascending order step-by-step."}
        ]),
        "prompts_json": json.dumps([
            "How many passes are required for n elements?",
            "How does early termination work when no swaps occur?"
        ]),
        "starter_input_json": json.dumps({"arr": [64, 34, 25, 12, 22]}),
        "starter_code_json": json.dumps({
            "python": "def bubble_sort(arr):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "bubble_sort",
        "test_cases_json": json.dumps([
            {"input": {"arr": [64, 34, 25, 12, 22]}, "expected": [12, 22, 25, 34, 64]}
        ]),
        "solution_code": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr"
    },
    {
        "id": "reverse-linked-list",
        "title": "Reverse Linked List",
        "difficulty": "Easy",
        "category": "Linked Lists",
        "pattern": "Linked List Pointers",
        "description": "Given the head of a singly linked list, reverse the list and return the reversed list.",
        "tags_json": json.dumps(["Linked List", "Recursion"]),
        "constraints_json": json.dumps(["0 <= nodes <= 5000"]),
        "examples_json": json.dumps([
            {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]", "explanation": "Reverses the direction of pointers in-place."}
        ]),
        "prompts_json": json.dumps([
            "What three pointers do we track during iterative reversal (prev, curr, next)?",
            "What is the base case for recursive reversal?"
        ]),
        "starter_input_json": json.dumps({"arr": [1, 2, 3, 4, 5]}),
        "starter_code_json": json.dumps({
            "python": "def reverse_list(head):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "reverse_list",
        "test_cases_json": json.dumps([
            {"input": {"arr": [1, 2, 3, 4, 5]}, "expected": [5, 4, 3, 2, 1]}
        ]),
        "solution_code": "def reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev"
    },
    {
        "id": "bfs",
        "title": "Breadth First Search (BFS)",
        "difficulty": "Medium",
        "category": "Graphs",
        "pattern": "Breadth First Search",
        "description": "Traverse graph level-by-level starting from a source node using a queue.",
        "tags_json": json.dumps(["Graph", "BFS", "Queue"]),
        "constraints_json": json.dumps(["1 <= nodes <= 1000"]),
        "examples_json": json.dumps([
            {"input": "graph = {0:[1,2], 1:[3], 2:[3]}, start = 0", "output": "[0, 1, 2, 3]", "explanation": "Visits node 0, then neighbours 1 and 2, then node 3."}
        ]),
        "prompts_json": json.dumps([
            "Why is Queue (FIFO) essential for level-order traversal?",
            "How do we prevent infinite cycles using a visited set?"
        ]),
        "starter_input_json": json.dumps({
            "graph": {0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6], 3: [1], 4: [1], 5: [2], 6: [2]},
            "start": 0
        }),
        "starter_code_json": json.dumps({
            "python": "def bfs(graph, start):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "bfs",
        "test_cases_json": json.dumps([
            {
                "input": {
                    "graph": {"0": [1, 2], "1": [0, 3], "2": [0, 3], "3": [1, 2]},
                    "start": "0"
                },
                "expected": ["0", "1", "2", "3"]
            }
        ]),
        "solution_code": "def bfs(graph, start):\n    visited = {start}\n    queue = [start]\n    order = []\n    while queue:\n        node = queue.pop(0)\n        order.append(node)\n        for nbr in graph.get(node, []):\n            if nbr not in visited:\n                visited.add(nbr)\n                queue.append(nbr)\n    return order"
    },
    {
        "id": "dfs",
        "title": "Depth First Search (DFS)",
        "difficulty": "Medium",
        "category": "Graphs",
        "pattern": "Depth First Search",
        "description": "Traverse graph by exploring as far as possible along each branch before backtracking using a stack.",
        "tags_json": json.dumps(["Graph", "DFS", "Stack"]),
        "constraints_json": json.dumps(["1 <= nodes <= 1000"]),
        "examples_json": json.dumps([
            {"input": "graph = {0:[1,2], 1:[3]}, start = 0", "output": "[0, 2, 1, 3]", "explanation": "Explores deep path before backtracking."}
        ]),
        "prompts_json": json.dumps([
            "How does the call stack or explicit LIFO stack drive DFS?",
            "What is backtracking?"
        ]),
        "starter_input_json": json.dumps({
            "graph": {0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6], 3: [1], 4: [1], 5: [2], 6: [2]},
            "start": 0
        }),
        "starter_code_json": json.dumps({
            "python": "def dfs(graph, start):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "dfs",
        "test_cases_json": json.dumps([
            {
                "input": {
                    "graph": {"0": [1, 2], "1": [0, 3], "2": [0, 3], "3": [1, 2]},
                    "start": "0"
                },
                "expected": ["0", "2", "3", "1"]
            }
        ]),
        "solution_code": "def dfs(graph, start):\n    visited = set()\n    stack = [start]\n    order = []\n    while stack:\n        node = stack.pop()\n        if node not in visited:\n            visited.add(node)\n            order.append(node)\n            for nbr in graph.get(node, []):\n                if nbr not in visited:\n                    stack.append(nbr)\n    return order"
    },
    {
        "id": "fibonacci-dp",
        "title": "Fibonacci Numbers (Dynamic Programming)",
        "difficulty": "Easy",
        "category": "Dynamic Programming",
        "pattern": "Dynamic Programming",
        "description": "Compute the n-th Fibonacci number using DP memoization or bottom-up tabulation.",
        "tags_json": json.dumps(["Dynamic Programming", "Recursion"]),
        "constraints_json": json.dumps(["0 <= n <= 45"]),
        "examples_json": json.dumps([
            {"input": "n = 7", "output": "13", "explanation": "0, 1, 1, 2, 3, 5, 8, 13."}
        ]),
        "prompts_json": json.dumps([
            "What are the base cases F(0)=0 and F(1)=1?",
            "How does tabulation convert O(2ⁿ) exponential recursion to O(n) linear time?"
        ]),
        "starter_input_json": json.dumps({"n": 7}),
        "starter_code_json": json.dumps({
            "python": "def fib(n):\n    # Write your solution here\n    pass"
        }),
        "entry_function": "fib",
        "test_cases_json": json.dumps([
            {"input": {"n": 7}, "expected": 13},
            {"input": {"n": 0}, "expected": 0},
            {"input": {"n": 1}, "expected": 1}
        ]),
        "solution_code": "def fib(n):\n    if n <= 1: return n\n    dp = [0] * (n + 1)\n    dp[1] = 1\n    for i in range(2, n + 1):\n        dp[i] = dp[i-1] + dp[i-2]\n    return dp[n]"
    }
]


def seed_database():
    from Backend.database import Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[DataSeeder] Seeding DSA problems into SQLite database …")
        for p in PROBLEMS_DATA:
            try:
                existing = db.query(Problem).filter(Problem.id == p["id"]).first()
            except Exception:
                db.rollback()
                existing = None

            if not existing:
                problem = Problem(**p)
                db.add(problem)
            else:
                for k, v in p.items():
                    setattr(existing, k, v)
        db.commit()

        # Seed Demo User if not present
        demo_user = db.query(User).filter(User.email == "demo@algomentor.com").first()
        if not demo_user:
            user = User(
                email="demo@algomentor.com",
                name="Alex Chen",
                password_hash=hash_password("demo123"),
                level="Intermediate"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            knowledge = StudentKnowledge(
                user_id=user.id,
                mastered_topics_json=json.dumps(["Arrays", "Sorting"]),
                weak_topics_json=json.dumps(["Graphs", "Dynamic Programming"]),
                streak_days=7,
                solved_count=5
            )
            db.add(knowledge)
            db.commit()

        print("[DataSeeder] Database seeded successfully ✅")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
