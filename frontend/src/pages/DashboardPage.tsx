import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ChartPanel } from "../components/ChartPanel";
import { StatCard } from "../components/StatCard";
import type { ClientOut, DashboardSummary } from "../types";

const currencyFormatter = new Intl.NumberFormat("nl-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export function DashboardPage() {
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | "all">("all");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listClients().then(setClients).catch(() => setError("Could not load clients."));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const clientId = selectedClientId === "all" ? undefined : selectedClientId;
    api
      .dashboardSummary(clientId)
      .then(setSummary)
      .catch(() => setError("Could not load dashboard data."))
      .finally(() => setLoading(false));
  }, [selectedClientId]);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Headcount, gross pay, and employer cost across your clients.</p>
      </div>

      {error && <p className="empty-state">{error}</p>}

      <div className="controls-row">
        <label htmlFor="client-select" style={{ color: "var(--ink-soft)", fontSize: 13.5 }}>
          Client
        </label>
        <select
          id="client-select"
          value={selectedClientId}
          onChange={(event) =>
            setSelectedClientId(event.target.value === "all" ? "all" : Number(event.target.value))
          }
        >
          <option value="all">All clients</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <div className="stat-row">
        <StatCard label="Total client count" value={summary ? String(summary.total_client_count) : "—"} />
      </div>

      {!loading && summary && (
        <div className="chart-grid">
          <ChartPanel title="Headcount" data={summary.headcount_series} valueLabel="Employees" />
          <ChartPanel
            title="Total gross"
            data={summary.total_gross_series}
            valueLabel="Total gross"
            formatValue={(v) => currencyFormatter.format(v)}
          />
          <ChartPanel
            title="Employer cost"
            data={summary.employer_cost_series}
            valueLabel="Employer cost"
            formatValue={(v) => currencyFormatter.format(v)}
          />
        </div>
      )}
    </div>
  );
}
