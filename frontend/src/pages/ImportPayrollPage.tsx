import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ClientOut, ImportResult } from "../types";

const currencyFormatter = new Intl.NumberFormat("nl-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export function ImportPayrollPage() {
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [years, setYears] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [period, setPeriod] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    api.listClients().then((list) => {
      setClients(list);
      setSelectedClientId(list[0]?.id ?? null);
    });
    api.availableYears().then((list) => {
      setYears(list);
      setSelectedYear(list[0] ?? new Date().getFullYear());
    });
  }, []);

  async function handleImport() {
    setResult(null);
    if (!selectedClientId || !selectedYear || !period.trim() || !file) {
      setStatus("Choose a client, year, and period, and select a file.");
      return;
    }
    setImporting(true);
    setStatus(null);
    try {
      const outcome = await api.importPayroll(selectedClientId, selectedYear, period.trim(), file);
      setResult(outcome);
      setStatus(null);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setImporting(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Import payroll</h1>
        <p>Select the client, year, and period, then upload the payroll file.</p>
      </div>

      <div className="panel" style={{ maxWidth: 460 }}>
        <div className="controls-row" style={{ marginBottom: 14 }}>
          <label style={{ color: "var(--ink-soft)", fontSize: 13.5, minWidth: 55 }}>Client</label>
          <select
            value={selectedClientId ?? ""}
            onChange={(e) => setSelectedClientId(Number(e.target.value))}
          >
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="controls-row" style={{ marginBottom: 14 }}>
          <label style={{ color: "var(--ink-soft)", fontSize: 13.5, minWidth: 55 }}>Year</label>
          <select value={selectedYear ?? ""} onChange={(e) => setSelectedYear(Number(e.target.value))}>
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
            {selectedYear && !years.includes(selectedYear) && (
              <option value={selectedYear}>{selectedYear}</option>
            )}
          </select>
        </div>

        <div className="controls-row" style={{ marginBottom: 14 }}>
          <label style={{ color: "var(--ink-soft)", fontSize: 13.5, minWidth: 55 }}>Period</label>
          <input
            type="text"
            placeholder="e.g. 2026-05"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            style={{
              padding: "7px 12px",
              borderRadius: 3,
              border: "1px solid var(--line-strong)",
              fontSize: 13.5,
              fontFamily: "var(--font-ui)",
            }}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <p style={{ marginTop: 6, color: "var(--ink-faint)", fontSize: 12.5 }}>
            CSV columns: employee_id, employee_name, annual_gross_salary, actual_net_salary
          </p>
        </div>

        <button onClick={handleImport} disabled={importing}>
          {importing ? "Importing…" : "Import"}
        </button>

        {status && <p style={{ marginTop: 14, color: "var(--status-flag)", fontSize: 13.5 }}>{status}</p>}

        {result && (
          <div style={{ marginTop: 18, borderTop: "1px solid var(--line)", paddingTop: 14 }}>
            <p style={{ fontSize: 13.5, marginBottom: 6 }}>Import complete.</p>
            <p style={{ fontSize: 13.5, color: "var(--ink-soft)", margin: "2px 0" }}>
              Headcount: {result.headcount}
            </p>
            <p style={{ fontSize: 13.5, color: "var(--ink-soft)", margin: "2px 0" }}>
              Total gross: {currencyFormatter.format(result.total_gross)}
            </p>
            <p style={{ fontSize: 13.5, color: "var(--ink-soft)", margin: "2px 0" }}>
              Employer cost: {currencyFormatter.format(result.employer_cost)}
            </p>
            <p style={{ fontSize: 13.5, color: "var(--status-flag)", margin: "2px 0" }}>
              Flagged for review: {result.flagged_count}
            </p>
            <p style={{ fontSize: 12.5, color: "var(--ink-faint)", marginTop: 8 }}>
              Check the Dashboard and Exception Review pages to see this reflected.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
