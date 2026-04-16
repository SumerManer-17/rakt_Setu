// ─────────────────────────────────────────
// RaktSetu — API Helper
// All frontend → backend calls go here
// ─────────────────────────────────────────

const API_BASE = "http://localhost:5000";

async function apiCall(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" }
  };
  if (body) options.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  return await response.json();
}

// ── DONOR APIs ──
const DonorAPI = {
  register: (data)         => apiCall("/api/donors/register", "POST", data),
  getProfile: (phone)      => apiCall(`/api/donors/${phone}`),
  update: (phone, data)    => apiCall(`/api/donors/${phone}`, "PUT", data),
  toggleStatus: (phone)    => apiCall(`/api/donors/${phone}/toggle`, "PATCH"),
  getActive: (bloodGroup)  => apiCall(`/api/donors/active${bloodGroup ? "?blood_group=" + bloodGroup : ""}`)
};

// ── REQUEST APIs ──
const RequestAPI = {
  postEmergency: (data)    => apiCall("/api/requests/emergency", "POST", data),
  getStatus: (id)          => apiCall(`/api/requests/${id}/status`),
  getOpen: (bloodGroup)    => apiCall(`/api/requests/open${bloodGroup ? "?blood_group=" + bloodGroup : ""}`),
  cancel: (id)             => apiCall(`/api/requests/${id}/cancel`, "PATCH")
};

// ── ADMIN APIs ──
const AdminAPI = {
  getStats:       () => apiCall("/api/admin/stats"),
  getAllDonors:    () => apiCall("/api/admin/donors"),
  getAllRequests:  () => apiCall("/api/admin/requests"),
  getBloodGroups: () => apiCall("/api/admin/blood-groups")
};