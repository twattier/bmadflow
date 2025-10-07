import { Home, FileText, MessageSquare, Settings, FolderTree } from 'lucide-react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { useAppStore } from '@/store/appStore';
import { useEffect } from 'react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const location = useLocation();
  const { selectedProjectId, setSelectedProjectId } = useAppStore();

  // Extract projectId from URL path since useParams doesn't work outside Route components
  const projectIdFromPath = location.pathname.match(/^\/projects\/([^/]+)/)?.[1];

  // Update selected project ID when route changes
  useEffect(() => {
    if (projectIdFromPath) {
      setSelectedProjectId(projectIdFromPath);
    }
  }, [projectIdFromPath, setSelectedProjectId]);

  const isActive = (path: string) => location.pathname === path;

  // Determine if we're in a project context
  const inProjectContext = !!projectIdFromPath || !!selectedProjectId;
  const currentProjectId = projectIdFromPath || selectedProjectId;

  return (
    <aside className="w-64 border-r bg-card">
      <div className="p-6">
        <h1 className="text-2xl font-bold">BMADFlow</h1>
      </div>
      <nav className="space-y-2 p-4">
        {inProjectContext && currentProjectId ? (
          // Project-specific navigation
          <>
            <Link
              to={`/projects/${currentProjectId}`}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive(`/projects/${currentProjectId}`) && 'bg-accent'
              )}
            >
              <FileText className="h-5 w-5" />
              <span>Overview</span>
            </Link>
            <Link
              to={`/projects/${currentProjectId}/explorer`}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive(`/projects/${currentProjectId}/explorer`) && 'bg-accent'
              )}
            >
              <FolderTree className="h-5 w-5" />
              <span>Explorer</span>
            </Link>
            <Link
              to={`/projects/${currentProjectId}/chat`}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive(`/projects/${currentProjectId}/chat`) && 'bg-accent'
              )}
            >
              <MessageSquare className="h-5 w-5" />
              <span>Chat</span>
            </Link>
            <Link
              to={`/projects/${currentProjectId}/settings`}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive(`/projects/${currentProjectId}/settings`) && 'bg-accent'
              )}
            >
              <Settings className="h-5 w-5" />
              <span>Settings</span>
            </Link>
            <div className="pt-4 border-t mt-4">
              <Link
                to="/"
                onClick={() => setSelectedProjectId(null)}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                  isActive('/') && 'bg-accent'
                )}
              >
                <Home className="h-5 w-5" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
          </>
        ) : (
          // Global navigation
          <>
            <Link
              to="/"
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive('/') && 'bg-accent'
              )}
            >
              <Home className="h-5 w-5" />
              <span>Dashboard</span>
            </Link>
            <Link
              to="/projects"
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive('/projects') && 'bg-accent'
              )}
            >
              <FileText className="h-5 w-5" />
              <span>Projects</span>
            </Link>
            <Link
              to="/config"
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent',
                isActive('/config') && 'bg-accent'
              )}
            >
              <Settings className="h-5 w-5" />
              <span>Configuration</span>
            </Link>
          </>
        )}
      </nav>
    </aside>
  );
}
