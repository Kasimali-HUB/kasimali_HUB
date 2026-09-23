import type {
  ClientOut,
  DashboardSummary,
  ExceptionPayload,
  ImportResult,
  LegislationAnswer,
  PayrollRun,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(body || `Request to ${path} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listClients: () => request<ClientOut[]>("/clients"),

  dashboardSummary: (clientId?: number) =>
    request<DashboardSummary>(clientId ? `/dashboard/summary?client_id=${clientId}` : "/dashboard/summary"),

  availableYears: () => request<number[]>("/payroll-runs/years"),

  listPayrollRuns: () => request<PayrollRun[]>("/payroll-runs"),

  exceptionsDemo: () => request<ExceptionPayload[]>("/exceptions/demo"),

  exceptionsForRun: (clientId: number, year: number, period: string) =>
    request<ExceptionPayload[]>(
      `/exceptions?client_id=${clientId}&year=${year}&period=${encodeURIComponent(period)}`
    ),

  importPayroll: async (clientId: number, year: number, period: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const params = new URLSearchParams({
      client_id: String(clientId),
      year: String(year),
      period,
    });
    // No Content-Type header here on purpose - the browser sets the
    // multipart boundary itself; overriding it breaks the upload.
    const response = await fetch(`${API_BASE}/payroll-runs/import?${params}`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const body = await response.text().catch(() => "");
      throw new Error(body || `Import failed: ${response.status}`);
    }
    return response.json() as Promise<ImportResult>;
  },

  askLegislation: (question: string) =>
    request<LegislationAnswer>("/legislation/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
};
