import { useEffect, useState } from "react";
import { api } from "../api/client";
import { StatCard } from "../components/StatCard";
import type { ExceptionPayload, PayrollRun } from "../types";

const currencyFormatter = new Intl.NumberFormat("nl-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat("nl-NL", {
  style: "percent",
  maximumFractionDigits: 1,
  signDisplay: "always",
});

function runKey(run: PayrollRun) {
  return `${run.client_id}|${run.year}|${run.period}`;
}

export function ExceptionTriagePage() {
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [selectedRunKey, setSelectedRunKey] = useState<string | null>(null);
  const [payloads, setPayloads] = useState<ExceptionPayload[]>([]);
  const [usingSampleData, setUsingSampleData] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listPayrollRuns()
      .then((result) => {
        setRuns(result);
        if (result.length > 0) {
          setSelectedRunKey(runKey(result[0]));
        } else {
          setUsingSampleData(true);
        }
      })
      .catch(() => setError("Could not load payroll runs."));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);

    if (!selectedRunKey) {
      // No real runs imported yet - show sample data, clearly labeled.
      api
        .exceptionsDemo()
        .then((result) => {
          setPayloads([...result].sort((a, b) => Number(b.flagged) - Number(a.flagged)));
          setUsingSampleData(true);
        })
        .catch(() => setError("Could not load the exception queue."))
        .finally(() => setLoading(false));
      return;
    }

    const [clientId, year, period] = selectedRunKey.split("|");
    api
      .exceptionsForRun(Number(clientId), Number(year), period)
      .then((result) => {
        setPayloads([...result].sort((a, b) => Number(b.flagged) - Number(a.flagged)));
        setUsingSampleData(false);
      })
      .catch(() => setError("Could not load the exception queue."))
      .finally(() => setLoading(false));
  }, [selectedRunKey]);

  const flaggedCount = payloads.filter((p) => p.flagged).length;

  return (
    <div>
      <div className="page-header">
        <h1>Exception review</h1>
        <p>Every payslip is checked automatically; only variances beyond tolerance need a look.</p>
      </div>

      {error && <p className="empty-state">{error}</p>}

      {runs.length > 0 && (
        <div className="field-group" style={{ maxWidth: 320 }}>
          <label htmlFor="run-select">Run</label>
          <select id="run-select" value={selectedRunKey ?? ""} onChange={(e) => setSelectedRunKey(e.target.value)}>
            {runs.map((run) => (
              <option key={runKey(run)} value={runKey(run)}>
                {run.client_name} — {run.period}
              </option>
            ))}
          </select>
        </div>
      )}

      {usingSampleData && (
        <p className="hint" style={{ marginBottom: 16 }}>
          No payroll has been imported yet — showing sample data. Import a run on the Import
          Payroll page to see real results here.
        </p>
      )}

      {!loading && (
        <div className="stat-row">
          <StatCard label="Processed" value={String(payloads.length)} />
          <StatCard label="Flagged for review" value={String(flaggedCount)} />
          <StatCard label="Auto-cleared" value={String(payloads.length - flaggedCount)} />
        </div>
      )}

      <div className="panel">
        <table>
          <thead>
            <tr>
              <th>Employee</th>
              <th className="numeric">Gross</th>
              <th className="numeric">Expected net</th>
              <th className="numeric">Actual net</th>
              <th className="numeric">Variance</th>
            </tr>
          </thead>
          <tbody>
            {payloads.map((p) => (
              <tr key={p.employee_token}>
                <td>{p.employee_token}</td>
                <td className="numeric">{currencyFormatter.format(p.annual_gross_salary)}</td>
                <td className="numeric">{currencyFormatter.format(p.expected_net_salary)}</td>
                <td className="numeric">{currencyFormatter.format(p.actual_net_salary)}</td>
                <td className="numeric">
                  <span className={`badge ${p.flagged ? "flag" : "ok"}`}>
                    {percentFormatter.format(p.variance_pct)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
