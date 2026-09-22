export interface ClientOut {
  id: number;
  name: string;
  country_code: string;
}

export interface ChartPoint {
  period: string;
  year: number;
  value: number;
}

export interface DashboardSummary {
  total_client_count: number;
  selected_client_id: number | null;
  headcount_series: ChartPoint[];
  total_gross_series: ChartPoint[];
  employer_cost_series: ChartPoint[];
}

export interface ExceptionPayload {
  employee_token: string;
  run_id: string;
  annual_gross_salary: number;
  expected_net_salary: number;
  actual_net_salary: number;
  variance_pct: number;
  flagged: boolean;
}

export interface SourceCitation {
  doc_id: string;
  title: string;
  citation: string;
}

export interface LegislationAnswer {
  question: string;
  answer: string;
  sources: SourceCitation[];
  generated_by_llm: boolean;
}
