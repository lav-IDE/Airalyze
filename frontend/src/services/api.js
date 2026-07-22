// Production builds must provide VITE_API_BASE_URL (for example
// https://api.example.com).  The same-origin default works with a reverse
// proxy in production and Vite's /api proxy during local development.
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 12_000;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
      ...options,
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(payload?.detail || `Request failed (${response.status})`);
    }
    if (payload === null || (typeof payload !== "object" && typeof payload !== "string" && typeof payload !== "number" && typeof payload !== "boolean")) {
      throw new Error("The API returned an invalid payload");
    }
    return payload;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The forecast service did not respond in time");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getForecast(wardId) {
  const forecast = await request(`/forecast/${encodeURIComponent(wardId)}`);
  if (!forecast || typeof forecast !== "object" || Array.isArray(forecast) || typeof forecast.forecast_aqi !== "number" || !forecast.aqi_band) {
    throw new Error("The API forecast response is missing required fields");
  }
  return forecast;
}
export async function getWards() {
  return request("/wards/");
}

export async function getAdvisory(wardId, userProfile) {
  return request(`/advisory/${encodeURIComponent(wardId)}`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ user_profile: userProfile }),
  });
}

export async function publishAdvisory(wardId, language, profile, text) {
  return request(`/advisory/publish`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({
      ward_id: wardId,
      language: language,
      age_group: profile.age_group,
      health_condition: profile.health_conditions[0],
      activity: profile.activity,
      advisory_text: text,
    }),
  });
}
