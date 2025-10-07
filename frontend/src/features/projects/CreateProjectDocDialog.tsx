import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { useCreateProjectDoc } from '@/api/hooks/useProjectDocs';

interface CreateProjectDocDialogProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateProjectDocDialog({
  projectId,
  open,
  onOpenChange,
}: CreateProjectDocDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [githubFolderPath, setGithubFolderPath] = useState('');
  const [errors, setErrors] = useState<{
    name?: string;
    githubUrl?: string;
  }>({});

  const createProjectDoc = useCreateProjectDoc(projectId);

  const validateForm = () => {
    const newErrors: { name?: string; githubUrl?: string } = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    } else if (name.length > 255) {
      newErrors.name = 'Name must be 255 characters or less';
    }

    if (!githubUrl.trim()) {
      newErrors.githubUrl = 'GitHub URL is required';
    } else {
      // Basic URL validation
      try {
        const url = new URL(githubUrl);
        if (!url.hostname.includes('github.com')) {
          newErrors.githubUrl = 'Must be a valid GitHub URL';
        }
      } catch {
        newErrors.githubUrl = 'Must be a valid URL';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await createProjectDoc.mutateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
        github_url: githubUrl.trim(),
        github_folder_path: githubFolderPath.trim() || undefined,
      });

      // Reset form and close dialog on success
      setName('');
      setDescription('');
      setGithubUrl('');
      setGithubFolderPath('');
      setErrors({});
      onOpenChange(false);
    } catch {
      // Error is handled by mutation's onError
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Clear form when closing
      setName('');
      setDescription('');
      setGithubUrl('');
      setGithubFolderPath('');
      setErrors({});
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Add Documentation Source</DialogTitle>
          <DialogDescription>Add a GitHub repository to sync documentation from.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (errors.name) setErrors({ ...errors, name: undefined });
                }}
                placeholder="e.g., API Documentation"
                maxLength={255}
                data-testid="projectdoc-name-input"
              />
              {errors.name && (
                <p className="text-sm text-destructive" data-testid="name-error">
                  {errors.name}
                </p>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="github-url">
                GitHub URL <span className="text-destructive">*</span>
              </Label>
              <Input
                id="github-url"
                value={githubUrl}
                onChange={(e) => {
                  setGithubUrl(e.target.value);
                  if (errors.githubUrl) setErrors({ ...errors, githubUrl: undefined });
                }}
                placeholder="https://github.com/owner/repo"
                data-testid="github-url-input"
              />
              {errors.githubUrl && (
                <p className="text-sm text-destructive" data-testid="github-url-error">
                  {errors.githubUrl}
                </p>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="github-folder-path">
                Folder Path <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="github-folder-path"
                value={githubFolderPath}
                onChange={(e) => setGithubFolderPath(e.target.value)}
                placeholder="e.g., docs/ or docs/api/"
                data-testid="github-folder-path-input"
              />
              <p className="text-xs text-muted-foreground">Leave empty to sync entire repository</p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter description (optional)"
                rows={3}
                data-testid="projectdoc-description-input"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={createProjectDoc.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createProjectDoc.isPending}
              data-testid="create-projectdoc-button"
            >
              {createProjectDoc.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                'Add Source'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
