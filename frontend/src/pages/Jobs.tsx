import { useEffect, useState } from "react";
import { fetchJobs } from "../api/jobs";
import JobCard from "../components/JobCard";
import { Job, JobFilters } from "../types";

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<JobFilters>({ page: 1, page_size: 10 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchJobs(filters)
      .then((res) => {
        setJobs(res.items);
        setTotal(res.total);
        setError("");
      })
      .catch(() => setError("Failed to load jobs"))
      .finally(() => setLoading(false));
  }, [filters]);

  function updateFilter<K extends keyof JobFilters>(key: K, value: JobFilters[K]) {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h1>Find your next role</h1>
      <div style={styles.filterBar}>
        <input
          placeholder="Search title, company, description..."
          onChange={(e) => updateFilter("q", e.target.value)}
        />
        <input placeholder="Location" onChange={(e) => updateFilter("location", e.target.value)} />
        <input placeholder="Skill" onChange={(e) => updateFilter("skill", e.target.value)} />
        <select
          onChange={(e) =>
            updateFilter("employment_type", (e.target.value || undefined) as JobFilters["employment_type"])
          }
        >
          <option value="">Any type</option>
          <option value="full_time">Full time</option>
          <option value="part_time">Part time</option>
          <option value="contract">Contract</option>
          <option value="internship">Internship</option>
        </select>
        <input
          type="number"
          placeholder="Min salary"
          onChange={(e) => updateFilter("min_salary", Number(e.target.value) || undefined)}
        />
      </div>

      {loading && <p>Loading jobs...</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {!loading && jobs.length === 0 && <p>No jobs match your filters.</p>}

      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}

      <p style={{ color: "#777" }}>
        Showing {jobs.length} of {total} results
      </p>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  filterBar: {
    display: "flex",
    gap: 8,
    flexWrap: "wrap",
    marginBottom: 24,
  },
};
