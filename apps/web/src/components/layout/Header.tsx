import { useProject } from '../../stores/ProjectContext';
import { Breadcrumbs } from './Breadcrumbs';

export default function Header() {
  const { currentProject } = useProject();

  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-6">
              {/* BMADFlow Logo */}
              <h1 className="text-2xl font-bold text-primary">BMADFlow</h1>

              {/* Project Name */}
              {currentProject && (
                <div className="text-sm text-muted-foreground">
                  Project: <span className="font-medium text-foreground">{currentProject.name}</span>
                </div>
              )}
            </div>

            {/* Breadcrumb Navigation */}
            {currentProject && <Breadcrumbs />}
          </div>

          {/* Sync Status Indicator */}
          {currentProject && (
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${
                currentProject.sync_status === 'idle' ? 'bg-green-500' :
                currentProject.sync_status === 'syncing' ? 'bg-yellow-500 animate-pulse' :
                'bg-red-500'
              }`}></div>
              <span className="text-sm text-muted-foreground capitalize">{currentProject.sync_status}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
