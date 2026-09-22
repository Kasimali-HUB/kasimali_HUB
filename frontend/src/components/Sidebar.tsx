import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/import", label: "Import payroll" },
  { to: "/exceptions", label: "Exception review" },
];

export function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-title">GPIP</div>
      <div className="sidebar-nav">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) => (isActive ? "active" : undefined)}
          >
            {link.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
