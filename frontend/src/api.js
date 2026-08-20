const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function readError(res) {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    return JSON.stringify(data.detail || data);
  } catch {
    return res.statusText || "Request failed";
  }
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend is not reachable");
  return res.json();
}

/* ----------------------------- User / Candidates ---------------------------- */

export async function getUsers() {
  const res = await fetch(`${API_BASE}/api/users`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getUserById(userId) {
  const res = await fetch(`${API_BASE}/api/users/${userId}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createUser({ name, targetRole, email, file }) {
  const form = new FormData();
  form.append("name", name.trim());
  form.append("target_role", (targetRole || "Software Engineer").trim());
  if (email) form.append("email", email.trim());
  if (file) form.append("file", file);

  const res = await fetch(`${API_BASE}/api/users`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateUser(userId, { name, targetRole, email }) {
  const res = await fetch(`${API_BASE}/api/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, target_role: targetRole, email }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteUser(userId) {
  const res = await fetch(`${API_BASE}/api/users/${userId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function uploadUserResume(userId, file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/users/${userId}/resume`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function reanalyzeUser(userId) {
  const res = await fetch(`${API_BASE}/api/users/${userId}/reanalyze`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getUserResume(userId) {
  const res = await fetch(`${API_BASE}/api/users/${userId}/resume`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getUserAnalysis(userId) {
  const res = await fetch(`${API_BASE}/api/users/${userId}/analysis`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

/* ----------------------------- Sessions & History ---------------------------- */

export async function getLatestSession(userId = null) {
  const params = userId ? `?user_id=${userId}` : "";
  const res = await fetch(`${API_BASE}/api/session/latest${params}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getHistory(userId = null) {
  const params = userId ? `?user_id=${userId}` : "";
  const res = await fetch(`${API_BASE}/api/history${params}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function loadSampleDemo() {
  const res = await fetch(`${API_BASE}/api/demo/load-sample`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function loginUser({ userId = null, email = null, name = null }) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, email, name }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function registerUser({ name, email = null, targetRole = "" }) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, target_role: targetRole }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getUsersList() {
  const res = await fetch(`${API_BASE}/api/auth/users`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function uploadResume({ file, name, targetRole, userId }) {
  const form = new FormData();
  form.append("file", file);
  form.append("name", name || "Demo User");
  form.append("target_role", targetRole || "");
  if (userId) form.append("user_id", String(userId));

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function saveResumeText({ rawText, name, targetRole, userId }) {
  const res = await fetch(`${API_BASE}/api/resume/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      raw_text: rawText,
      name: name || "Demo User",
      target_role: targetRole || "",
      user_id: userId || null,
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function fetchJobs(role, location, userId = null, resumeId = null) {
  const params = new URLSearchParams({ role, location });
  if (userId) params.append("user_id", String(userId));
  if (resumeId) params.append("resume_id", String(resumeId));

  const res = await fetch(`${API_BASE}/api/jobs?${params}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function analyzeGaps({ resumeText, jobDescriptions, userId, resumeId, name, targetRole }) {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: resumeText,
      job_descriptions: jobDescriptions,
      user_id: userId || null,
      resume_id: resumeId || null,
      name: name || "Demo User",
      target_role: targetRole || "",
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function generateLesson(skill, skillGapId = null) {
  const res = await fetch(`${API_BASE}/api/generate-lesson`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skill,
      skill_gap_id: skillGapId || null,
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function checkCode(submittedCode, solutionCode, lessonId = null, concept = "") {
  const res = await fetch(`${API_BASE}/api/check-code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      submitted_code: submittedCode,
      solution_code: solutionCode,
      lesson_id: lessonId || null,
      concept: concept || "",
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function sendGapChat(skillGapId, message) {
  const res = await fetch(`${API_BASE}/api/gap-chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skill_gap_id: skillGapId,
      message,
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getLessonAttempts(lessonId) {
  const res = await fetch(`${API_BASE}/api/lessons/${lessonId}/attempts`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getVerifiedProof(userIdentifier) {
  const res = await fetch(`${API_BASE}/api/proof/${userIdentifier}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getPlatformStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function getSupportedRoles() {
  const res = await fetch(`${API_BASE}/api/roles`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}
