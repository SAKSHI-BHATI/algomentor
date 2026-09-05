const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const getHeaders = () => {
  const token = localStorage.getItem("algomentor_token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

// ---------------- PROBLEMS API ----------------
export const fetchProblems = async () => {
  try {
    const res = await fetch(`${BASE_URL}/problems`, { headers: getHeaders() });
    return await res.json();
  } catch (err) {
    console.warn("fetchProblems fallback:", err);
    return { success: false, error: err.message };
  }
};

export const fetchProblemDetails = async (problemId) => {
  try {
    const res = await fetch(`${BASE_URL}/problems/${problemId}`, { headers: getHeaders() });
    return await res.json();
  } catch (err) {
    console.warn("fetchProblemDetails fallback:", err);
    return { success: false, error: err.message };
  }
};

// ---------------- PROGRESS & DASHBOARD ----------------
export const saveUserProgress = async (problemId, status, whiteboardContent, flowchartData, conceptBreakdown) => {
  try {
    const res = await fetch(`${BASE_URL}/progress/save`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        problem_id: problemId,
        status: status,
        whiteboard_content: whiteboardContent,
        flowchart_data: flowchartData,
        concept_breakdown: conceptBreakdown,
      }),
    });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const fetchUserProgress = async (problemId) => {
  try {
    const res = await fetch(`${BASE_URL}/progress/${problemId}`, { headers: getHeaders() });
    return await res.json();
  } catch (err) {
    return { success: false, progress: null };
  }
};

export const fetchDashboardData = async () => {
  try {
    const res = await fetch(`${BASE_URL}/dashboard`, { headers: getHeaders() });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

// ---------------- UNDERSTANDING ----------------
export const checkUnderstanding = async (text, problemId, description) => {
  const res = await fetch(`${BASE_URL}/understanding`, {
    method: "POST",
    headers: getHeaders(),
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
    headers: getHeaders(),
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
    headers: getHeaders(),
    body: JSON.stringify({
      problem_id: problemId,
      thought: thought,
      thinking_state: thinkingState,
      problem_description: description,
    }),
  });
  return res.json();
};

// ---------------- EVALUATE & SIMULATE ----------------
export const evaluateCode = async (code, description = "") => {
  const res = await fetch(`${BASE_URL}/evaluate`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ code, problem_description: description }),
  });
  return res.json();
};

export const simulateAlgorithm = async (problemId, code, inputData = {}, useOptimal = false) => {
  const res = await fetch(`${BASE_URL}/simulate`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      problem_id: problemId,
      code: code,
      input_data: inputData,
      use_optimal: useOptimal,
    }),
  });
  return res.json();
};

// ---------------- 9-STAGE MENTOR PIPELINE API ----------------
export const fetchMentorUnderstand = async (problemId, statement = "", constraints = "") => {
  try {
    const res = await fetch(`${BASE_URL}/mentor/${problemId}/understand`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ statement, constraints }),
    });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const fetchMentorPatternHint = async (problemId, userThoughts = "", codeDraft = "") => {
  try {
    const res = await fetch(`${BASE_URL}/mentor/${problemId}/pattern-hint`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ user_thoughts: userThoughts, code_draft: codeDraft }),
    });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const fetchMentorBridge = async (problemId, thought = "", code = "") => {
  try {
    const res = await fetch(`${BASE_URL}/mentor/${problemId}/bridge`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ thought, code }),
    });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

export const fetchMentorReview = async (problemId, code, language = "python", testResults = null) => {
  try {
    const res = await fetch(`${BASE_URL}/mentor/${problemId}/review`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ code, language, test_results: testResults }),
    });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
};

// ---------------- SANDBOXED CODE EXECUTION API ----------------
export const executeSolutionCode = async (problemId, code, language = "python") => {
  try {
    const res = await fetch(`${BASE_URL}/execute/${problemId}`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ code, language }),
    });
    return await res.json();
  } catch (err) {
    return { status: "error", message: err.message, all_passed: false };
  }
};

