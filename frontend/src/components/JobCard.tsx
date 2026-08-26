import { Link } from "react-router-dom";
import { Job } from "../types";

export default function JobCard({ job }: { job: Job }) {
  return (
    <div style={styles.card}>
      <h3 style={{ margin: "0 0 4px" }}>
        <Link to={`/jobs/${job.id}`}>{job.title}</Link>
      </h3>
      <p style={{ margin: "0 0 8px", color: "#555" }}>
        {job.company} &middot; {job.location} &middot; {job.employment_type.replace("_", " ")}
      </p>
      {(job.salary_min || job.salary_max) && (
        <p style={{ margin: "0 0 8px" }}>
          ${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()}
        </p>
      )}
      <p style={{ margin: 0, fontSize: "0.85rem", color: "#777" }}>{job.skills}</p>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    border: "1px solid #e2e2e2",
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
};
