import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import type { Project } from '@/api/types/project';
import { useProjectDocs } from '@/api/hooks/useProjectDocs';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate();
  const { data: projectDocs } = useProjectDocs(project.id);
  const projectDocCount = projectDocs?.length ?? 0;

  const handleViewClick = () => {
    navigate(`/projects/${project.id}`);
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" data-testid="project-card">
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
        {project.description && (
          <CardDescription className="line-clamp-2">{project.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <span className="text-sm text-muted-foreground">
            {projectDocCount} {projectDocCount === 1 ? 'document' : 'documents'}
          </span>
          <Button onClick={handleViewClick} size="sm" data-testid="view-button">
            View
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
