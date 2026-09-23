import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ClientOut, ImportResult } from "../types";

const currencyFormatter = new Intl.NumberFormat("nl-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function buildPeriod(year: number, month: number): string {
  return `${year}-${String(month).padStart(2, "0")}`;
}

export function ImportPayrollPage() {
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [years, setYears] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
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
      const currentYear = new Date().getFullYear();
      // Always offer the current year and the next one, even if no data
      // has been imported for them yet - otherwise a brand-new year would
      // never be selectable until something existed for it already.
      const withUpcoming = Array.from(new Set([currentYear, currentYear + 1, ...list])).sort(
        (a, b) => b - a
      );
      setYears(withUpcoming);
      setSelectedYear(withUpcoming[0]);
    });
  }, []);

  async function handleImport() {
    setResult(null);
    if (!selectedClientId || !selectedYear || !file) {
      setStatus("Choose a client, year, and month, and select a file.");
      return;
    }
    setImporting(true);
    setStatus(null);
    try {
      const period = buildPeriod(selectedYear, selectedMonth);
      const outcome = await api.importPayroll(selectedClientId, selectedYear, period, file);
      setResult(outcome);
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
        <p>Select the client, year, and month, then upload the payroll file.</p>
      </div>

      <div className="panel" style={{ maxWidth: 460 }}>
        <div className="field-group">
          <label htmlFor="import-client">Client</label>
          <select
            id="import-client"
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

        <div className="field-row" style={{ marginBottom: 16 }}>
          <div className="field-group" style={{ marginBottom: 0 }}>
            <label htmlFor="import-year">Year</label>
            <select
              id="import-year"
              value={selectedYear ?? ""}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
            >
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>

          <div className="field-group" style={{ marginBottom: 0 }}>
            <label htmlFor="import-month">Month</label>
            <select
              id="import-month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
            >
              {MONTHS.map((name, index) => (
                <option key={name} value={index + 1}>
                  {name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field-group">
          <label htmlFor="import-file">Payroll file</label>
          <input
            id="import-file"
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <p className="hint">
            CSV columns: employee_id, employee_name, annual_gross_salary, actual_net_salary
          </p>
        </div>

        <button onClick={handleImport} disabled={importing}>
          {importing ? "Importing…" : "Import"}
        </button>

        {status && <p className="status-message">{status}</p>}

        {result && (
          <div className="result-panel">
            <p className="result-heading">
              Import complete — {selectedYear && buildPeriod(selectedYear, selectedMonth)}
            </p>
            <div className="result-row">
              <span>Headcount</span>
              <span className="value">{result.headcount}</span>
            </div>
            <div className="result-row">
              <span>Total gross</span>
              <span className="value">{currencyFormatter.format(result.total_gross)}</span>
            </div>
            <div className="result-row">
              <span>Employer cost</span>
              <span className="value">{currencyFormatter.format(result.employer_cost)}</span>
            </div>
            <div className="result-row flagged">
              <span>Flagged for review</span>
              <span className="value">{result.flagged_count}</span>
            </div>
            <p className="hint" style={{ marginTop: 10 }}>
              Check the Dashboard and Exception Review pages to see this reflected.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
