import { useState } from 'react';
import { useProjects } from '@/api/hooks/useProjects';
import { ProjectCard } from '@/features/projects/ProjectCard';
import { CreateProjectDialog } from '@/features/projects/CreateProjectDialog';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { EmptyState } from '@/components/common/EmptyState';
import { Card, CardContent } from '@/components/ui/card';
import { Plus } from 'lucide-react';

export function Projects() {
  const { data: projects, isLoading, error } = useProjects();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  const hasProjects = projects && projects.length > 0;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Projects</h1>

      {!hasProjects ? (
        <EmptyState message="No projects yet. Create your first project to get started." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}

          {/* "+ New Project" card */}
          <Card
            className="hover:shadow-lg transition-shadow cursor-pointer border-dashed"
            onClick={() => setIsCreateDialogOpen(true)}
            data-testid="new-project-card"
          >
            <CardContent className="flex flex-col items-center justify-center h-full min-h-[200px]">
              <Plus className="h-12 w-12 text-muted-foreground mb-2" />
              <p className="text-muted-foreground font-medium">New Project</p>
            </CardContent>
          </Card>
        </div>
      )}

      {!hasProjects && (
        <div className="flex justify-center mt-6">
          <Card
            className="hover:shadow-lg transition-shadow cursor-pointer border-dashed w-full max-w-sm"
            onClick={() => setIsCreateDialogOpen(true)}
            data-testid="new-project-card"
          >
            <CardContent className="flex flex-col items-center justify-center h-full min-h-[200px]">
              <Plus className="h-12 w-12 text-muted-foreground mb-2" />
              <p className="text-muted-foreground font-medium">New Project</p>
            </CardContent>
          </Card>
        </div>
      )}

      <CreateProjectDialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen} />
    </div>
  );
}
