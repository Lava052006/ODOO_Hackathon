const API_BASE = "http://127.0.0.1:8000/api"

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  }

  if (options.body instanceof FormData) {
    delete headers["Content-Type"]
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "omit"
  })

  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { error: response.statusText }
    }
    const errorMessage = errorData.error || errorData.detail || errorData.message || (typeof errorData === "string" ? errorData : Object.values(errorData)[0]) || "Request failed"
    throw new Error(Array.isArray(errorMessage) ? errorMessage[0] : errorMessage)
  }

  return response.json()
}

export const authApi = {
  signin: (email, password, remember = true) =>
    request("/auth/signin/", {
      method: "POST",
      body: JSON.stringify({ email, password, remember })
    }),
  signup: (data) =>
    request("/auth/signup/", {
      method: "POST",
      body: JSON.stringify(data)
    }),
  verifyOtp: (data) =>
    request("/auth/verify/", {
      method: "POST",
      body: JSON.stringify(data)
    }),
  me: () => request("/auth/me/"),
  logout: () => request("/auth/logout/", { method: "POST" })
}

export const employeeApi = {
  getAll: () => request("/employees/"),
  getSummary: () => request("/employees/summary/"),
  get: (employeeId) => request(`/employees/${employeeId}/`),
  update: (employeeId, data) =>
    request(`/employees/${employeeId}/`, {
      method: "PATCH",
      body: JSON.stringify(data)
    }),
  uploadDocument: (employeeId, formData) =>
    request(`/employees/${employeeId}/documents/`, {
      method: "POST",
      body: formData
    })
}

export const attendanceApi = {
  getSummary: () => request("/attendance/summary/"),
  toggleCheckin: () => request("/attendance/toggle-checkin/", { method: "POST" }),
  getMyWeek: () => request("/attendance/my-week/"),
  exportCsvUrl: () => `${API_BASE}/attendance/export/`
}

export const leavesApi = {
  getDashboard: (status = "pending") => request(`/leaves/?status=${status}`),
  submit: (data) =>
    request("/leaves/submit/", {
      method: "POST",
      body: JSON.stringify(data)
    }),
  resolve: (id, status, comment = "") =>
    request(`/leaves/${id}/decision/`, {
      method: "POST",
      body: JSON.stringify({ status, comment })
    })
}

export const payrollApi = {
  getSummary: () => request("/payroll/summary/"),
  updateSalary: (employeeId, data) =>
    request(`/payroll/employees/${employeeId}/`, {
      method: "POST",
      body: JSON.stringify(data)
    }),
  runCheck: () => request("/payroll/run-check/", { method: "POST" }),
  exportReportUrl: () => `${API_BASE}/payroll/export-report/`
}

export const rosterApi = {
  getDashboard: () => request("/roster/"),
  updateShift: (employeeId, date, code) =>
    request("/roster/update-shift/", {
      method: "POST",
      body: JSON.stringify({ employeeId, date, code })
    }),
  publish: () => request("/roster/publish/", { method: "POST" })
}

export const coreApi = {
  getCommandCentre: () => request("/dashboard/command-centre/"),
  getNotifications: () => request("/notifications/"),
  markNotificationsRead: () => request("/notifications/mark-read/", { method: "POST" }),
  savePreferences: (preferences) =>
    request("/notifications/preferences/", {
      method: "POST",
      body: JSON.stringify({ preferences })
    })
}
