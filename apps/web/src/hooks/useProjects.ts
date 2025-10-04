import { useMutation, useQuery } from '@tanstack/react-query';
import { getProject, createProject, triggerSync, getSyncStatus } from '../services/projectsService';
import type { Project, SyncStatusResponse } from '../types/project';

export function useProjectById(projectId: string | null) {
  return useQuery<Project>({
    queryKey: ['project', projectId],
    queryFn: () => getProject(projectId!),
    enabled: !!projectId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateProject() {
  return useMutation({
    mutationFn: (githubUrl: string) => createProject(githubUrl),
  });
}

export function useTriggerSync() {
  return useMutation({
    mutationFn: (projectId: string) => triggerSync(projectId),
  });
}

export function useSyncStatus(projectId: string | null, enabled: boolean = true) {
  return useQuery<SyncStatusResponse>({
    queryKey: ['sync-status', projectId],
    queryFn: () => getSyncStatus(projectId!),
    enabled: enabled && !!projectId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'in_progress' ? 2000 : false;
    },
  });
}
