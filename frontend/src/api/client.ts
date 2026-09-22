const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Request to ${path} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listClients: () => request<import("../types").ClientOut[]>("/clients"),

  dashboardSummary: (clientId?: number) =>
    request<import("../types").DashboardSummary>(
      clientId ? `/dashboard/summary?client_id=${clientId}` : "/dashboard/summary"
    ),

  availableYears: () => request<number[]>("/payroll-runs/years"),

  exceptionsDemo: () => request<import("../types").ExceptionPayload[]>("/exceptions/demo"),

  askLegislation: (question: string) =>
    request<import("../types").LegislationAnswer>("/legislation/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
};
