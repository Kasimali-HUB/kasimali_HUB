import { useEffect, useState } from "react";
import { ClientSelect } from "../components/ClientSelect";
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

const CURRENT_YEAR = new Date().getFullYear();
// Shown immediately, before the API call returns (or even if it fails) -
// a brand-new year should always be pickable, not dependent on network data.
const DEFAULT_YEARS = [CURRENT_YEAR + 1, CURRENT_YEAR];

export function ImportPayrollPage() {
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [years, setYears] = useState<number[]>(DEFAULT_YEARS);
  const [selectedYear, setSelectedYear] = useState<number>(CURRENT_YEAR);
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [yearsWarning, setYearsWarning] = useState<string | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    api
      .listClients()
      .then((list) => {
        setClients(list);
        setSelectedClientId((current) => current ?? list[0]?.id ?? null);
      })
      .catch(() => setStatus("Could not load clients. Check that the backend is running."));

    api
      .availableYears()
      .then((list) => {
        const merged = Array.from(new Set([...DEFAULT_YEARS, ...list])).sort((a, b) => b - a);
        setYears(merged);
      })
      .catch(() => {
        // DEFAULT_YEARS is already showing, so the dropdown still works -
        // just flag that past years' data may not be reflected.
        setYearsWarning("Could not load past import years - showing this year and next only.");
      });
  }, []);

  function handleClientCreated(newClient: ClientOut) {
    setClients((prev) => [...prev, newClient].sort((a, b) => a.name.localeCompare(b.name)));
    setSelectedClientId(newClient.id);
  }

  async function handleImport() {
    setResult(null);
    if (!selectedClientId || !file) {
      setStatus("Choose a client and a file first.");
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

      <div className="panel" style={{ maxWidth: 480 }}>
        <ClientSelect
          id="import-client"
          clients={clients}
          value={selectedClientId !== null ? String(selectedClientId) : ""}
          onChange={(v) => setSelectedClientId(v ? Number(v) : null)}
          onClientCreated={handleClientCreated}
        />

        <div className="field-row" style={{ marginBottom: 16 }}>
          <div className="field-group" style={{ marginBottom: 0 }}>
            <label htmlFor="import-year">Year</label>
            <select
              id="import-year"
              value={selectedYear}
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
        {yearsWarning && <p className="hint" style={{ marginTop: -10, marginBottom: 16 }}>{yearsWarning}</p>}

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
              Import complete — {buildPeriod(selectedYear, selectedMonth)}
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
