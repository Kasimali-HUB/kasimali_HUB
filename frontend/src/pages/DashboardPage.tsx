import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ChartPanel } from "../components/ChartPanel";
import { ClientSelect } from "../components/ClientSelect";
import { StatCard } from "../components/StatCard";
import type { ClientOut, DashboardSummary } from "../types";

const currencyFormatter = new Intl.NumberFormat("nl-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export function DashboardPage() {
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [selectedValue, setSelectedValue] = useState("all");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listClients().then(setClients).catch(() => setError("Could not load clients."));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const clientId = selectedValue === "all" ? undefined : Number(selectedValue);
    api
      .dashboardSummary(clientId)
      .then(setSummary)
      .catch(() => setError("Could not load dashboard data."))
      .finally(() => setLoading(false));
  }, [selectedValue]);

  function handleClientCreated(newClient: ClientOut) {
    setClients((prev) => [...prev, newClient].sort((a, b) => a.name.localeCompare(b.name)));
    setSelectedValue(String(newClient.id));
  }

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Headcount, gross pay, and employer cost across your clients.</p>
      </div>

      {error && <p className="empty-state">{error}</p>}

      <div style={{ maxWidth: 380 }}>
        <ClientSelect
          id="client-select"
          clients={clients}
          value={selectedValue}
          onChange={setSelectedValue}
          onClientCreated={handleClientCreated}
          leadingOption={{ value: "all", label: "All clients" }}
        />
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
