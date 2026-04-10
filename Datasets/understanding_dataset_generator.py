import random
import json
import re

# -------------------------
# CONFIG
# -------------------------
NUM_SAMPLES = 250

problems = ["Two Sum", "Valid Parentheses", "Binary Search", "Fibonacci", "Graph Traversal"]

# -------------------------
# TEMPLATES
# -------------------------

correct = {
    "Two Sum": ["use hashmap to store complements", "check target difference using map"],
    "Valid Parentheses": ["use stack to match brackets", "push pop using stack"],
    "Binary Search": ["use mid and divide search space", "check middle and eliminate half"],
    "Fibonacci": ["use dp or memoization", "store previous results"],
    "Graph Traversal": ["use bfs or dfs", "traverse using queue or recursion"]
}

weak = [
    "i am not sure what to do",
    "maybe try something",
    "i think brute force maybe",
    "not clear",
    "idk logic",
    "confused between methods"
]

wrong = {
    "Two Sum": [
        "use graph traversal",
        "apply bfs and hashmap together",
        "use dfs to find pair",
        "sort then use binary search"
    ],
    "Valid Parentheses": [
        "use binary search",
        "sort brackets",
        "use dp array",
        "count brackets only"
    ],
    "Binary Search": [
        "scan entire array",
        "use bfs to find element",
        "use hashmap",
        "brute force recursion"
    ],
    "Fibonacci": [
        "use binary search",
        "sort numbers first",
        "use bfs",
        "use hashmap"
    ],
    "Graph Traversal": [
        "use binary search",
        "sort array first",
        "use dp only",
        "use hashmap only"
    ]
}

# -------------------------
# HUMANIZER
# -------------------------

prefix = ["i think", "maybe", "idk but", "i guess", ""]
suffix = ["", " i guess", " maybe", " not sure"]
noise  = ["", "", " yaar", " confused hu"]

def humanize(text):
    text = f"{random.choice(prefix)} {text}".strip()
    text += random.choice(suffix)
    text += random.choice(noise)
    return text.strip()

# -------------------------
# MIXED CONFUSION (KEY 🔥)
# -------------------------

def mixed(problem):
    c = random.choice(correct[problem])
    w = random.choice(wrong[problem])
    return random.choice([
        f"{c} but also {w}",
        f"{w} and maybe {c}",
        f"{c} or maybe {w}"
    ])

# -------------------------
# DATA GENERATION
# -------------------------

dataset = []

for _ in range(NUM_SAMPLES):
    problem = random.choice(problems)
    r = random.random()

    if r < 0.4:
        thought = random.choice(wrong[problem])
        label = "WATCH"

    elif r < 0.7:
        thought = random.choice(weak)
        label = "WATCH"

    elif r < 0.85:
        thought = mixed(problem)
        label = "WATCH"

    else:
        thought = random.choice(correct[problem])
        label = "PROCEED"

    thought = humanize(thought)

    dataset.append({
        "input": f"Problem: {problem} | Thought: {thought}",
        "label": label
    })

# -------------------------
# SAVE
# -------------------------
import os

# SAVE
file_path = "Datasets/understanding_dataset.json"

with open(file_path, "w") as f:
    json.dump(dataset, f, indent=2)

print("Dataset generated:", len(dataset))
print("Saved at:", os.path.abspath(file_path))

# NOW REOPEN FOR READING ✅
with open(file_path, "r") as f:
    check = json.load(f)

print("First entry:", check[0])
print("Total entries:", len(check))