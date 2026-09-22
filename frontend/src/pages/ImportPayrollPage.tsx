import { useEffect, useState } from "react";
import { api } from "../api/client";

export function ImportPayrollPage() {
  const [years, setYears] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    api
      .availableYears()
      .then((result) => {
        setYears(result);
        setSelectedYear(result[0] ?? null);
      })
      .catch(() => setStatus("Could not load available years."));
  }, []);

  function handleImport() {
    if (!selectedYear || !fileName) {
      setStatus("Choose a year and a file first.");
      return;
    }
    // No backend import endpoint exists yet - this is the UI shape only.
    setStatus(`Ready to import "${fileName}" for ${selectedYear}. Import endpoint not wired up yet.`);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Import payroll</h1>
        <p>Select the year, then upload the payroll file for that period.</p>
      </div>

      <div className="panel" style={{ maxWidth: 420 }}>
        <div className="controls-row" style={{ marginBottom: 16 }}>
          <label htmlFor="year-select" style={{ color: "var(--ink-soft)", fontSize: 13.5, minWidth: 40 }}>
            Year
          </label>
          <select
            id="year-select"
            value={selectedYear ?? ""}
            onChange={(event) => setSelectedYear(Number(event.target.value))}
          >
            {years.length === 0 && <option value="">No years available</option>}
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: 16 }}>
          <input
            type="file"
            onChange={(event) => setFileName(event.target.files?.[0]?.name ?? null)}
          />
        </div>

        <button onClick={handleImport}>Import</button>

        {status && (
          <p style={{ marginTop: 14, color: "var(--ink-soft)", fontSize: 13.5 }}>{status}</p>
        )}
      </div>
    </div>
  );
}
