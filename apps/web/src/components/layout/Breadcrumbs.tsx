import { Link, useLocation, useParams } from 'react-router-dom';
import { useDocument } from '../../hooks/useDocuments';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string; // Undefined for current page
}

/**
 * Breadcrumb navigation component
 * Shows: Project > Current View > Document Title
 */
export function Breadcrumbs() {
  const location = useLocation();
  const { documentId } = useParams<{ documentId: string }>();
  const { data: document } = useDocument(documentId || '');

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Project', href: '/' }
  ];

  // Determine view name from route
  if (location.pathname.startsWith('/scoping')) {
    breadcrumbs.push({ label: 'Scoping', href: '/scoping' });
  } else if (location.pathname.startsWith('/epics')) {
    breadcrumbs.push({ label: 'Epics', href: '/epics' });
  } else if (location.pathname.startsWith('/architecture')) {
    breadcrumbs.push({ label: 'Architecture', href: '/architecture' });
  } else if (location.pathname.startsWith('/detail')) {
    breadcrumbs.push({ label: 'Detail' });
  }

  // Add document title if in Detail view and document is loaded
  if (documentId && document) {
    breadcrumbs.push({ label: document.title });
  }

  return (
    <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
      <ol className="flex items-center gap-1">
        {breadcrumbs.map((item, index) => {
          const isLast = index === breadcrumbs.length - 1;

          return (
            <li key={index} className="flex items-center gap-1">
              {item.href ? (
                <Link
                  to={item.href}
                  className="hover:text-foreground transition-colors"
                >
                  {item.label}
                </Link>
              ) : (
                <span className={isLast ? 'font-medium text-foreground' : ''}>
                  {item.label}
                </span>
              )}
              {!isLast && <ChevronRight className="h-4 w-4" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
