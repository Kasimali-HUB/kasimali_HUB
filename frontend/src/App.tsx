import { Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { DashboardPage } from "./pages/DashboardPage";
import { ExceptionTriagePage } from "./pages/ExceptionTriagePage";
import { ImportPayrollPage } from "./pages/ImportPayrollPage";

export function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/import" element={<ImportPayrollPage />} />
          <Route path="/exceptions" element={<ExceptionTriagePage />} />
        </Routes>
      </main>
    </div>
  );
}
