import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useProject } from '@/api/hooks/useProjects';
import { useProjectDocs } from '@/api/hooks/useProjectDocs';
import { ProjectDocCard } from '@/features/projects/ProjectDocCard';
import { CreateProjectDocDialog } from '@/features/projects/CreateProjectDocDialog';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export function ProjectOverview() {
  const { projectId } = useParams<{ projectId: string }>();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const { data: project, isLoading: projectLoading, error: projectError } = useProject(projectId!);

  const {
    data: projectDocs,
    isLoading: docsLoading,
    error: docsError,
  } = useProjectDocs(projectId!);

  if (projectLoading || docsLoading) {
    return <LoadingSpinner />;
  }

  if (projectError || docsError) {
    return <ErrorDisplay error={(projectError || docsError) as Error} />;
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">{project?.name}</h1>
        {project?.description && <p className="text-muted-foreground">{project.description}</p>}
      </div>

      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-2xl font-semibold">Documentation Sources</h2>
        <Button variant="outline" onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add ProjectDoc
        </Button>
      </div>

      {projectDocs && projectDocs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projectDocs.map((projectDoc) => (
            <ProjectDocCard key={projectDoc.id} projectDoc={projectDoc} />
          ))}
        </div>
      ) : (
        <div className="text-center p-8 border-2 border-dashed rounded-lg">
          <p className="text-muted-foreground">
            No documentation sources configured. Add a ProjectDoc to sync documentation from GitHub.
          </p>
        </div>
      )}

      <CreateProjectDocDialog
        projectId={projectId!}
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />
    </div>
  );
}
