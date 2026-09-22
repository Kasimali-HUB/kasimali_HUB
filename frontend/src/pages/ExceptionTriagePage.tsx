import { useEffect, useState } from "react";
import { api } from "../api/client";
import { StatCard } from "../components/StatCard";
import type { ExceptionPayload } from "../types";

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

export function ExceptionTriagePage() {
  const [payloads, setPayloads] = useState<ExceptionPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .exceptionsDemo()
      .then((result) => {
        // Flagged rows surface first - that's the point of exception-based review.
        setPayloads([...result].sort((a, b) => Number(b.flagged) - Number(a.flagged)));
      })
      .catch(() => setError("Could not load the exception queue."))
      .finally(() => setLoading(false));
  }, []);

  const flaggedCount = payloads.filter((p) => p.flagged).length;

  return (
    <div>
      <div className="page-header">
        <h1>Exception review</h1>
        <p>Every payslip is checked automatically; only variances beyond tolerance need a look.</p>
      </div>

      {error && <p className="empty-state">{error}</p>}

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
              <th></th>
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
                <td></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
