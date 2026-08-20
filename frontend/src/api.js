/**
 * SkillBridge AI - API Client Module
 * Connects frontend to the FastAPI backend at http://127.0.0.1:8000
 */

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

/* ----------------------------- Health & System ----------------------------- */

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend is not reachable");
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

export async function assessPosition(position, country = "United States", resumeText = "") {
  const res = await fetch(`${API_BASE}/api/users/assess-position`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      position: position || "Software Engineer",
      country: country || "United States",
      resume_text: resumeText || "",
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function translateSkill(duty, targetRole = "AI Operations Specialist", country = "United States") {
  const res = await fetch(`${API_BASE}/api/translate-skill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      duty: duty || "",
      target_role: targetRole || "AI Operations Specialist",
      country: country || "United States",
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
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

export async function createUser(data) {
  if (data instanceof FormData || data?.file) {
    const form = data instanceof FormData ? data : new FormData();
    if (!(data instanceof FormData)) {
      form.append("name", (data.name || "New Candidate").trim());
      form.append("target_role", (data.position || data.targetRole || data.target_role || "AI Operations Specialist").trim());
      form.append("position", (data.position || data.targetRole || data.target_role || "AI Operations Specialist").trim());
      if (data.country) form.append("country", data.country);
      if (data.countryCode || data.country_code) form.append("country_code", data.countryCode || data.country_code);
      if (data.currency) form.append("currency", data.currency);
      if (data.currencyCode || data.currency_code) form.append("currency_code", data.currencyCode || data.currency_code);
      if (data.currencySymbol || data.currency_symbol) form.append("currency_symbol", data.currencySymbol || data.currency_symbol);
      if (data.email) form.append("email", data.email.trim());
      if (data.currentRole || data.current_role) form.append("current_role", (data.currentRole || data.current_role).trim());
      if (data.location) form.append("location", data.location.trim());
      if (data.currentSalary || data.current_salary) form.append("current_salary", data.currentSalary || data.current_salary);
      if (data.targetSalary || data.target_salary) form.append("target_salary", data.targetSalary || data.target_salary);
      if (data.file) form.append("file", data.file);
    }
    const res = await fetch(`${API_BASE}/api/users/upload`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(await readError(res));
    return res.json();
  }

  const payload = {
    name: (data.name || "New Candidate").trim(),
    email: data.email ? data.email.trim() : null,
    current_role: (data.currentRole || data.current_role || "Customer Support Team Lead").trim(),
    target_role: (data.position || data.targetRole || data.target_role || "AI Operations & Support Systems Specialist").trim(),
    position: (data.position || data.targetRole || data.target_role || "AI Operations & Support Systems Specialist").trim(),
    location: (data.location || "Austin, TX (or Remote)").trim(),
    country: data.country || "United States",
    country_code: data.countryCode || data.country_code || "US",
    currency: data.currency || "US Dollar",
    currency_code: data.currencyCode || data.currency_code || "USD",
    currency_symbol: data.currencySymbol || data.currency_symbol || "$",
    avatar: data.avatar || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80",
    current_salary: data.currentSalary || data.current_salary || "$50,000",
    target_salary: data.targetSalary || data.target_salary || "$90,000",
    experience_years: parseFloat(data.experienceYears || data.experience_years || 4),
    automation_risk_score: parseInt(data.automationRiskScore || data.automation_risk_score || 75),
    shielded_risk_score: parseInt(data.shieldedRiskScore || data.shielded_risk_score || 15),
    tasks_at_risk: data.tasksAtRisk || data.tasks_at_risk || [],
    skills_radar: data.skillsRadar || data.skills_radar || [],
    salary_growth: data.salaryGrowth || data.salary_growth || [],
    translated_skills: data.translatedSkills || data.translated_skills || [],
    raw_text: data.rawText || data.raw_text || "",
  };

  const res = await fetch(`${API_BASE}/api/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateUser(userId, data) {
  const payload = {
    name: data.name,
    email: data.email,
    current_role: data.currentRole !== undefined ? data.currentRole : data.current_role,
    target_role: (data.position !== undefined ? data.position : data.targetRole !== undefined ? data.targetRole : data.target_role),
    position: (data.position !== undefined ? data.position : data.targetRole !== undefined ? data.targetRole : data.target_role),
    location: data.location,
    country: data.country,
    country_code: data.countryCode || data.country_code,
    currency: data.currency,
    currency_code: data.currencyCode || data.currency_code,
    currency_symbol: data.currencySymbol || data.currency_symbol,
    avatar: data.avatar,
    current_salary: data.currentSalary !== undefined ? data.currentSalary : data.current_salary,
    target_salary: data.targetSalary !== undefined ? data.targetSalary : data.target_salary,
    experience_years: data.experienceYears !== undefined ? parseFloat(data.experienceYears) : (data.experience_years !== undefined ? parseFloat(data.experience_years) : undefined),
    automation_risk_score: data.automationRiskScore !== undefined ? parseInt(data.automationRiskScore) : (data.automation_risk_score !== undefined ? parseInt(data.automation_risk_score) : undefined),
    shielded_risk_score: data.shieldedRiskScore !== undefined ? parseInt(data.shieldedRiskScore) : (data.shielded_risk_score !== undefined ? parseInt(data.shielded_risk_score) : undefined),
    tasks_at_risk: data.tasksAtRisk || data.tasks_at_risk,
    skills_radar: data.skillsRadar || data.skills_radar,
    salary_growth: data.salaryGrowth || data.salary_growth,
    translated_skills: data.translatedSkills || data.translated_skills,
  };

  const res = await fetch(`${API_BASE}/api/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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

/* ----------------------------- Resume & Analysis ---------------------------- */

export async function uploadResume({ file, name, targetRole, userId }) {
  const form = new FormData();
  form.append("file", file);
  form.append("name", name || "Demo User");
  form.append("target_role", targetRole || "Software Engineer");
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
      target_role: targetRole || "Software Engineer",
      user_id: userId || null,
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function fetchJobs(role, location, userId = null, resumeId = null) {
  const params = new URLSearchParams({ role: role || "Software Engineer", location: location || "Remote" });
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

/* ----------------------------- Lessons, Labs & Code ------------------------- */

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

export async function getLessonAttempts(lessonId) {
  const res = await fetch(`${API_BASE}/api/lessons/${lessonId}/attempts`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

/* ----------------------------- AI Grounded Tutor Chat ----------------------- */

export async function sendGapChat(skillGapId, message) {
  const res = await fetch(`${API_BASE}/api/gap-chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skill_gap_id: skillGapId || 1,
      message,
    }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

/* ----------------------------- Proof of Work & Dossier ---------------------- */

export async function getVerifiedProof(userIdentifier) {
  const res = await fetch(`${API_BASE}/api/proof/${userIdentifier}`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}
