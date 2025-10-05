export interface ProjectCreate {
  name: string;
  description: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

export interface Contributor {
  id: string;
  name: string;
  email: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  owner_name: string;
  contributors: Contributor[];
  created_at: string;
  updated_at: string;
}

export interface ContributorAdd {
  email: string;
}
