const BASE_URL = "http://127.0.0.1:8000/api";

// ---------------- UNDERSTANDING ----------------
export const checkUnderstanding = async (text, problemId, description) => {
  const res = await fetch(`${BASE_URL}/understanding`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: text,
      problem_id: problemId,
      problem_description: description,
    }),
  });

  return res.json();
};

// ---------------- HINT ----------------
export const getHint = async (problemId, code, thinkingState, description) => {
  const res = await fetch(`${BASE_URL}/hint`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      problem_id: problemId,
      code: code,
      thinking_state: thinkingState,
      problem_description: description,
    }),
  });

  return res.json();
};

// ---------------- NEXT STEP ----------------
export const getNextStep = async (problemId, thought, thinkingState, description) => {
  const res = await fetch(`${BASE_URL}/next-step`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      problem_id: problemId,
      thought: thought,
      thinking_state: thinkingState,
      problem_description: description,
    }),
  });

  return res.json();
};

// ---------------- EVALUATE ----------------
export const evaluateCode = async (code) => {
  const res = await fetch(`${BASE_URL}/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code }),
  });

  return res.json();
};

// ── NEW FUNCTION (only addition below this line) ───────────────────────────────

// ---------------- SIMULATE ----------------
export const simulateAlgorithm = async (problemId, code, inputData = {}, useOptimal = false) => {
  const res = await fetch(`${BASE_URL}/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      problem_id:  problemId,
      code:        code,
      input_data:  inputData,
      use_optimal: useOptimal,
    }),
  });

  return res.json();
};
