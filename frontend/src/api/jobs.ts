import { api } from "./client";
import { Application, Job, JobFilters, JobListResponse } from "../types";

export async function fetchJobs(filters: JobFilters): Promise<JobListResponse> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== "")
  );
  const { data } = await api.get<JobListResponse>("/jobs", { params });
  return data;
}

export async function fetchJob(id: number): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}`);
  return data;
}

export async function createJob(payload: Partial<Job>): Promise<Job> {
  const { data } = await api.post<Job>("/jobs", payload);
  return data;
}

export async function applyToJob(jobId: number, coverLetter: string): Promise<Application> {
  const { data } = await api.post<Application>("/applications", {
    job_id: jobId,
    cover_letter: coverLetter,
  });
  return data;
}

export async function fetchMyApplications(): Promise<Application[]> {
  const { data } = await api.get<Application[]>("/applications/me");
  return data;
}

export async function fetchApplicantsForJob(jobId: number): Promise<Application[]> {
  const { data } = await api.get<Application[]>(`/applications/job/${jobId}`);
  return data;
}

export async function updateApplicationStatus(
  applicationId: number,
  status: string
): Promise<Application> {
  const { data } = await api.put<Application>(`/applications/${applicationId}/status`, {
    status,
  });
  return data;
}
