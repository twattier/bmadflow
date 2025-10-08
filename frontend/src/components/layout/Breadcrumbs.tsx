import { useLocation, Link } from 'react-router-dom';
import { useProject } from '@/api/hooks/useProjects';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';

export function Breadcrumbs() {
  const location = useLocation();

  // Extract projectId from URL path since useParams doesn't work outside Route components
  const projectId = location.pathname.match(/^\/projects\/([^/]+)/)?.[1];

  // Only fetch project data if projectId exists (enabled: !!projectId is in useProject hook)
  const { data: project } = useProject(projectId!);

  // Parse the current path to generate breadcrumbs
  const pathSegments = location.pathname.split('/').filter(Boolean);

  // Extract file path from URL search params if present
  const searchParams = new URLSearchParams(location.search);
  const filePath = searchParams.get('file');

  // Define breadcrumb structure based on routes
  const getBreadcrumbs = () => {
    const crumbs: Array<{ label: string; path?: string }> = [];

    if (pathSegments.length === 0) {
      // Home/Dashboard - no breadcrumbs needed
      return crumbs;
    }

    if (pathSegments[0] === 'projects') {
      if (pathSegments.length === 1) {
        // /projects - just "Projects" as current page
        crumbs.push({ label: 'Projects' });
      } else if (pathSegments.length >= 2 && projectId && project) {
        // /projects/:projectId or /projects/:projectId/something
        crumbs.push({ label: 'Projects', path: '/projects' });

        if (pathSegments.length === 2) {
          // /projects/:projectId - project name is current page (not clickable)
          crumbs.push({ label: project.name });
        } else if (pathSegments.length === 3) {
          // /projects/:projectId/explorer - project name is clickable, sub-page is current
          crumbs.push({ label: project.name, path: `/projects/${projectId}` });
          const subPath = pathSegments[2];
          const label = subPath.charAt(0).toUpperCase() + subPath.slice(1);

          // If on explorer page and file is selected, show file path breadcrumbs
          if (subPath === 'explorer' && filePath) {
            crumbs.push({ label, path: `/projects/${projectId}/explorer` });

            // Split file path into segments and create breadcrumbs
            const fileSegments = filePath.split('/').filter(Boolean);
            fileSegments.forEach((segment, idx) => {
              const isLastSegment = idx === fileSegments.length - 1;
              // Only the last segment (file name) is not clickable
              if (isLastSegment) {
                crumbs.push({ label: segment });
              } else {
                // Directory segments are clickable (for future directory navigation)
                crumbs.push({ label: segment });
              }
            });
          } else {
            crumbs.push({ label });
          }
        }
      }
    } else if (pathSegments[0] === 'config') {
      crumbs.push({ label: 'Configuration' });
    }

    return crumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  if (breadcrumbs.length === 0) {
    return null;
  }

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === breadcrumbs.length - 1;

          return (
            <div key={crumb.label} className="flex items-center">
              {index > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {isLast || !crumb.path ? (
                  <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link to={crumb.path}>{crumb.label}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </div>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
}
