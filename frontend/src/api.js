/* ═══════════════════════════════════════════
   Axios instance with interceptors
   ═══════════════════════════════════════════ */
import axios from "axios";

const api = axios.create({
    /* In dev the Vite proxy rewrites /api → http://localhost:8000
       In production, set VITE_API_BASE_URL to the real backend URL. */
    baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
    timeout: 30_000,
});

/* ── Request interceptor: attach API key ─── */
api.interceptors.request.use((config) => {
    const key = import.meta.env.VITE_API_KEY || "changeme-in-production";
    config.headers["X-API-Key"] = key;
    return config;
});

/* ── Response interceptor: normalise errors ── */
api.interceptors.response.use(
    (res) => res,
    (error) => {
        if (error.response) {
            const { status, data } = error.response;
            const message =
                data?.detail || `Request failed with status ${status}`;

            if (status === 401) {
                return Promise.reject(
                    new Error("Unauthorised – check your API key or credentials.")
                );
            }
            return Promise.reject(new Error(message));
        }
        return Promise.reject(new Error("Network error – is the backend running?"));
    }
);

export default api;
