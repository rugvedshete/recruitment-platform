export type Role = "candidate" | "recruiter" | "admin";

export type EmploymentType = "full_time" | "part_time" | "contract" | "internship";

export type ApplicationStatus = "submitted" | "under_review" | "interview" | "rejected" | "hired";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  created_at: string;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string;
  skills: string;
  employment_type: EmploymentType;
  salary_min: number | null;
  salary_max: number | null;
  is_active: boolean;
  created_at: string;
  posted_by_id: number;
}

export interface JobListResponse {
  total: number;
  items: Job[];
}

export interface Application {
  id: number;
  job_id: number;
  candidate_id: number;
  cover_letter: string | null;
  status: ApplicationStatus;
  created_at: string;
}

export interface JobFilters {
  q?: string;
  location?: string;
  skill?: string;
  employment_type?: EmploymentType;
  min_salary?: number;
  max_salary?: number;
  page?: number;
  page_size?: number;
}
