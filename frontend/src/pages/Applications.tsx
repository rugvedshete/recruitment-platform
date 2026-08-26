import { useEffect, useState } from "react";
import { fetchMyApplications } from "../api/jobs";
import { Application } from "../types";

export default function Applications() {
  const [applications, setApplications] = useState<Application[]>([]);

  useEffect(() => {
    fetchMyApplications().then(setApplications);
  }, []);

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>My Applications</h1>
      {applications.length === 0 && <p>You haven't applied to any jobs yet.</p>}
      <ul>
        {applications.map((app) => (
          <li key={app.id} style={{ marginBottom: 12 }}>
            Job #{app.job_id} — status: <strong>{app.status.replace("_", " ")}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
