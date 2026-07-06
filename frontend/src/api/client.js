const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetail = "API Request Failed";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // ignore non-json error body
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const getHealth = () => request("/health");

export const getLocalDemo = () => request("/demo/local");

export const calculateCalories = (payload) => 
  request("/tools/calorie-target", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const calculateProtein = (payload) => 
  request("/tools/protein-target", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const suggestMeals = (payload) => 
  request("/tools/meal-suggestions", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const buildSummary = (payload) => 
  request("/summary/build", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const listEvals = () => request("/evals");

export const runEvals = () => 
  request("/evals/run", {
    method: "POST",
  });

export const getEvalReport = () => request("/evals/report");

// Profile & Log persistence endpoints
export const listProfiles = () => request("/profiles");

export const createProfile = (payload) => 
  request("/profiles", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getProfile = (userId) => request(`/profiles/${userId}`);

export const logBodyMetric = (payload) => 
  request("/logs/body", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getBodyLogs = (userId) => request(`/logs/body/${userId}`);

export const logWorkoutSet = (payload) => 
  request("/logs/workouts", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getWorkoutLogs = (userId) => request(`/logs/workouts/${userId}`);

export const logNutritionTarget = (payload) => 
  request("/logs/nutrition-targets", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getLatestNutritionTarget = (userId) => request(`/logs/nutrition-targets/${userId}/latest`);

export const logMeal = (payload) => 
  request("/logs/meals", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getMealLogs = (userId) => request(`/logs/meals/${userId}`);

export const logSafetyFlag = (payload) => 
  request("/logs/safety-flags", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getOpenSafetyFlags = (userId) => request(`/logs/safety-flags/${userId}/open`);

export const resolveSafetyFlag = (flagId) => 
  request(`/logs/safety-flags/${flagId}/resolve`, {
    method: "POST",
  });

export const getUserContext = (userId) => request(`/context/${userId}`);

