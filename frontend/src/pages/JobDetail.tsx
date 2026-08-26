import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { applyToJob, fetchJob } from "../api/jobs";
import { useAuth } from "../context/AuthContext";
import { Job } from "../types";

export default function JobDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    if (id) fetchJob(Number(id)).then(setJob);
  }, [id]);

  async function handleApply() {
    if (!job) return;
    try {
      await applyToJob(job.id, coverLetter);
      setStatus("Application submitted!");
    } catch (err: any) {
      setStatus(err.response?.data?.detail || "Failed to apply");
    }
  }

  if (!job) return <p style={{ padding: 24 }}>Loading...</p>;

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h1>{job.title}</h1>
      <p style={{ color: "#555" }}>
        {job.company} &middot; {job.location} &middot; {job.employment_type.replace("_", " ")}
      </p>
      {(job.salary_min || job.salary_max) && (
        <p>
          ${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}
        </p>
      )}
      <p>{job.skills}</p>
      <p style={{ whiteSpace: "pre-wrap" }}>{job.description}</p>

      {user?.role === "candidate" && (
        <div style={{ marginTop: 24, borderTop: "1px solid #eee", paddingTop: 16 }}>
          <h3>Apply for this job</h3>
          <textarea
            placeholder="Cover letter (optional)"
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
            rows={5}
            style={{ width: "100%" }}
          />
          <button onClick={handleApply} style={{ marginTop: 8 }}>
            Submit application
          </button>
          {status && <p>{status}</p>}
        </div>
      )}
    </div>
  );
}
