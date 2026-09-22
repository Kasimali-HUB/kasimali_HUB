import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartPoint } from "../types";

// Mirrors --accent in tokens.css. Recharts sets this as an SVG attribute
// rather than through a stylesheet, so a literal value is used here rather
// than var(--accent) to avoid relying on attribute-level custom-property
// resolution. Keep in sync with tokens.css if the palette changes.
const LINE_COLOR = "#234e42";

interface ChartPanelProps {
  title: string;
  data: ChartPoint[];
  valueLabel: string;
  formatValue?: (value: number) => string;
}

export function ChartPanel({ title, data, valueLabel, formatValue }: ChartPanelProps) {
  return (
    <div className="panel chart-panel">
      <h3>{title}</h3>
      {data.length === 0 ? (
        <p className="empty-state">No data for this selection yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
            {/* Period (which encodes the year, e.g. "2026-03") sits on the
                x-axis at the bottom of every chart, as required. */}
            <XAxis
              dataKey="period"
              tick={{ fontSize: 12, fill: "var(--ink-soft)" }}
              axisLine={{ stroke: "var(--line-strong)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "var(--ink-soft)" }}
              axisLine={false}
              tickLine={false}
              width={48}
            />
            <Tooltip
              formatter={(value) => {
                const numeric = typeof value === "number" ? value : Number(value);
                return [formatValue ? formatValue(numeric) : numeric, valueLabel];
              }}
              contentStyle={{
                background: "var(--surface)",
                border: "1px solid var(--line)",
                borderRadius: 3,
                fontSize: 12.5,
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              name={valueLabel}
              stroke={LINE_COLOR}
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
