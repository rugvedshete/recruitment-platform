import { useEffect, useState } from "react";
import { createJob, fetchApplicantsForJob, fetchJobs, updateApplicationStatus } from "../api/jobs";
import { useAuth } from "../context/AuthContext";
import { Application, ApplicationStatus, Job } from "../types";

const STATUS_OPTIONS: ApplicationStatus[] = [
  "submitted",
  "under_review",
  "interview",
  "rejected",
  "hired",
];

export default function Dashboard() {
  const { user } = useAuth();
  const [myJobs, setMyJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [applicants, setApplicants] = useState<Application[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    company: "",
    description: "",
    location: "",
    skills: "",
    salary_min: "",
    salary_max: "",
  });
  const [message, setMessage] = useState("");

  async function loadMyJobs() {
    // The public /jobs endpoint doesn't filter by owner, so we fetch broadly and
    // filter client-side. A dedicated "/jobs?mine=true" endpoint would be a
    // natural backend improvement (see README > Next steps).
    const res = await fetchJobs({ page: 1, page_size: 100 });
    setMyJobs(res.items.filter((j) => j.posted_by_id === user?.id));
  }

  useEffect(() => {
    if (user) loadMyJobs();
  }, [user]);

  async function loadApplicants(jobId: number) {
    setSelectedJobId(jobId);
    const apps = await fetchApplicantsForJob(jobId);
    setApplicants(apps);
  }

  async function handleCreateJob(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createJob({
        title: form.title,
        company: form.company,
        description: form.description,
        location: form.location,
        skills: form.skills,
        salary_min: form.salary_min ? Number(form.salary_min) : undefined,
        salary_max: form.salary_max ? Number(form.salary_max) : undefined,
      });
      setMessage("Job posted!");
      setShowForm(false);
      loadMyJobs();
    } catch {
      setMessage("Failed to post job");
    }
  }

  async function handleStatusChange(applicationId: number, status: ApplicationStatus) {
    await updateApplicationStatus(applicationId, status);
    if (selectedJobId) loadApplicants(selectedJobId);
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Recruiter Dashboard</h1>
      <button onClick={() => setShowForm((s) => !s)}>
        {showForm ? "Cancel" : "Post a new job"}
      </button>
      {message && <p>{message}</p>}

      {showForm && (
        <form onSubmit={handleCreateJob} style={{ display: "grid", gap: 8, margin: "16px 0" }}>
          <input placeholder="Title" required onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <input placeholder="Company" required onChange={(e) => setForm({ ...form, company: e.target.value })} />
          <input placeholder="Location" required onChange={(e) => setForm({ ...form, location: e.target.value })} />
          <input
            placeholder="Skills (comma-separated)"
            onChange={(e) => setForm({ ...form, skills: e.target.value })}
          />
          <textarea
            placeholder="Description"
            required
            rows={4}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="number"
              placeholder="Min salary"
              onChange={(e) => setForm({ ...form, salary_min: e.target.value })}
            />
            <input
              type="number"
              placeholder="Max salary"
              onChange={(e) => setForm({ ...form, salary_max: e.target.value })}
            />
          </div>
          <button type="submit">Publish job</button>
        </form>
      )}

      <h2>Your job postings</h2>
      {myJobs.length === 0 && <p>You haven't posted any jobs yet.</p>}
      <ul>
        {myJobs.map((job) => (
          <li key={job.id} style={{ marginBottom: 8 }}>
            {job.title} at {job.company}{" "}
            <button onClick={() => loadApplicants(job.id)}>View applicants</button>
          </li>
        ))}
      </ul>

      {selectedJobId && (
        <div style={{ marginTop: 24 }}>
          <h3>Applicants for job #{selectedJobId}</h3>
          {applicants.length === 0 && <p>No applicants yet.</p>}
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={styles.th}>Candidate ID</th>
                <th style={styles.th}>Cover letter</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>
            <tbody>
              {applicants.map((a) => (
                <tr key={a.id}>
                  <td style={styles.td}>{a.candidate_id}</td>
                  <td style={styles.td}>{a.cover_letter || "-"}</td>
                  <td style={styles.td}>
                    <select
                      value={a.status}
                      onChange={(e) =>
                        handleStatusChange(a.id, e.target.value as ApplicationStatus)
                      }
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  th: { textAlign: "left", borderBottom: "2px solid #ddd", padding: 8 },
  td: { borderBottom: "1px solid #eee", padding: 8 },
};
