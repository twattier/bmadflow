import apiClient from './apiClient';
import type { Project, SyncStatusResponse, SyncTriggerResponse } from '../types/project';

export async function createProject(githubUrl: string): Promise<Project> {
  const response = await apiClient.post<Project>('/projects', {
    github_url: githubUrl,
  });
  return response.data;
}

export async function triggerSync(projectId: string): Promise<SyncTriggerResponse> {
  const response = await apiClient.post<SyncTriggerResponse>(`/projects/${projectId}/sync`);
  return response.data;
}

export async function getSyncStatus(projectId: string): Promise<SyncStatusResponse> {
  const response = await apiClient.get<SyncStatusResponse>(`/projects/${projectId}/sync-status`);
  return response.data;
}
