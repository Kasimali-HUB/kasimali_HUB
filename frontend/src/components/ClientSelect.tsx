import { useState } from "react";
import { api } from "../api/client";
import type { ClientOut } from "../types";

interface ClientSelectProps {
  id: string;
  clients: ClientOut[];
  /** Current select value, as a string - "all" or a client id, caller's choice. */
  value: string;
  onChange: (value: string) => void;
  onClientCreated: (client: ClientOut) => void;
  /** Extra option rendered first, e.g. { value: "all", label: "All clients" }. */
  leadingOption?: { value: string; label: string };
}

export function ClientSelect({
  id,
  clients,
  value,
  onChange,
  onClientCreated,
  leadingOption,
}: ClientSelectProps) {
  const [addingNew, setAddingNew] = useState(false);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleCreate() {
    const name = newName.trim();
    if (!name) {
      setError("Enter a client name first.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const created = await api.createClient(name);
      onClientCreated(created);
      setNewName("");
      setAddingNew(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create client.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="field-group">
      <label htmlFor={id}>Client</label>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <select id={id} value={value} onChange={(e) => onChange(e.target.value)} style={{ flex: 1 }}>
          {leadingOption && <option value={leadingOption.value}>{leadingOption.label}</option>}
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button type="button" className="secondary" onClick={() => setAddingNew((v) => !v)}>
          {addingNew ? "Cancel" : "+ New client"}
        </button>
      </div>

      {addingNew && (
        <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center" }}>
          <input
            type="text"
            placeholder="Client name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            style={{ flex: 1 }}
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          />
          <button type="button" onClick={handleCreate} disabled={saving}>
            {saving ? "Adding…" : "Add"}
          </button>
        </div>
      )}
      {error && <p className="status-message">{error}</p>}
    </div>
  );
}
