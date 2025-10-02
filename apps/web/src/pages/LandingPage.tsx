import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProject } from '../stores/ProjectContext';
import { useCreateProject, useTriggerSync, useSyncStatus } from '../hooks/useProjects';
import { Loader2, AlertCircle, Check } from 'lucide-react';
import type { Project } from '../types/project';

// Regex pattern for GitHub URL validation
const GITHUB_URL_PATTERN = /^(https?:\/\/)?(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;

export default function LandingPage() {
  const [githubUrl, setGithubUrl] = useState('');
  const [validationError, setValidationError] = useState('');
  const [localProject, setLocalProject] = useState<Project | null>(null);

  const navigate = useNavigate();
  const { setCurrentProject } = useProject();
  const createProjectMutation = useCreateProject();
  const triggerSyncMutation = useTriggerSync();

  const { data: syncStatus } = useSyncStatus(
    localProject?.id || null,
    !!localProject
  );

  const validateGithubUrl = (url: string): boolean => {
    if (!url.trim()) {
      setValidationError('GitHub URL is required');
      return false;
    }

    if (!GITHUB_URL_PATTERN.test(url)) {
      setValidationError('Invalid GitHub URL format. Expected: github.com/org/repo');
      return false;
    }

    setValidationError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateGithubUrl(githubUrl)) {
      return;
    }

    try {
      // Create project
      const project = await createProjectMutation.mutateAsync(githubUrl);
      setLocalProject(project);
      setCurrentProject(project); // Update global context

      // Trigger sync
      await triggerSyncMutation.mutateAsync(project.id);
    } catch (error) {
      console.error('Failed to create project or trigger sync:', error);
    }
  };

  const handleRetry = async () => {
    if (!localProject) return;

    try {
      await triggerSyncMutation.mutateAsync(localProject.id);
    } catch (error) {
      console.error('Failed to retry sync:', error);
    }
  };

  // Handle sync completion
  if (syncStatus?.status === 'completed') {
    // Show success toast and redirect
    setTimeout(() => {
      navigate('/scoping');
    }, 1000);

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="text-center">
          <Check className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Sync Complete!</h2>
          <p className="text-muted-foreground">Redirecting to scoping view...</p>
        </div>
      </div>
    );
  }

  const isLoading = createProjectMutation.isPending || triggerSyncMutation.isPending;
  const isSyncing = syncStatus?.status === 'in_progress';
  const hasFailed = syncStatus?.status === 'failed';

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">BMADFlow</h1>
          <p className="text-muted-foreground">
            Load your documentation and start exploring
          </p>
        </div>

        <div className="border rounded-lg p-6 bg-card">
          <h2 className="text-xl font-semibold mb-4">Add Project</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Enter your GitHub repository URL to get started
          </p>

          {!localProject ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="github-url" className="block text-sm font-medium mb-2">
                  GitHub Repository URL
                </label>
                <input
                  id="github-url"
                  type="text"
                  placeholder="github.com/org/repo"
                  value={githubUrl}
                  onChange={(e) => {
                    setGithubUrl(e.target.value);
                    setValidationError('');
                  }}
                  disabled={isLoading}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                  aria-invalid={!!validationError}
                  aria-describedby={validationError ? 'url-error' : undefined}
                />
                {validationError && (
                  <p id="url-error" className="text-sm text-destructive mt-1">
                    {validationError}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                {isLoading ? 'Syncing...' : 'Sync Now'}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              {isSyncing && (
                <div className="text-center">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                  <p className="font-medium mb-2">
                    Syncing... {syncStatus.processed_count} of {syncStatus.total_count} documents processed
                  </p>
                  {syncStatus.processed_count > 0 && syncStatus.total_count > 0 && (
                    <div className="w-full bg-secondary rounded-full h-2 mb-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{
                          width: `${(syncStatus.processed_count / syncStatus.total_count) * 100}%`,
                        }}
                      />
                    </div>
                  )}
                </div>
              )}

              {hasFailed && (
                <div className="border border-destructive rounded-md p-4 bg-destructive/10">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-destructive mb-1">Sync Failed</h3>
                      <p className="text-sm text-destructive/90 mb-3">
                        {syncStatus.error_message || 'An error occurred during sync'}
                      </p>
                      {syncStatus.retry_allowed && (
                        <button
                          onClick={handleRetry}
                          disabled={triggerSyncMutation.isPending}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90 font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center gap-2"
                        >
                          {triggerSyncMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                          Retry
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
