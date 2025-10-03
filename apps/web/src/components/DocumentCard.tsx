import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Badge } from './ui/badge';
import type { Document } from '../types/document';

interface DocumentCardProps {
  document: Document;
}

function getStatusVariant(status: string | null) {
  if (!status) return 'outline';

  switch (status.toLowerCase()) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'info';
    case 'failed':
      return 'destructive';
    case 'pending':
    default:
      return 'secondary';
  }
}

export function DocumentCard({ document }: DocumentCardProps) {
  return (
    <Link
      to={`/detail/${document.id}`}
      className="block p-6 border rounded-lg hover:shadow-lg transition-shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary cursor-pointer bg-card"
    >
      {/* Title - AC3.1 */}
      <h3 className="text-lg font-semibold line-clamp-2 leading-[1.4]">
        {document.title}
      </h3>

      {/* Excerpt - AC3.2 */}
      <p className="text-sm text-muted-foreground line-clamp-3 mt-2">
        {document.excerpt}
      </p>

      {/* Footer with date and badge */}
      <div className="flex items-center justify-between mt-4">
        {/* Last modified date - AC3.3 */}
        <p className="text-xs text-muted-foreground">
          {formatDistanceToNow(new Date(document.last_modified), {
            addSuffix: true,
          })}
        </p>

        {/* Status badge - AC3.4 */}
        {document.extraction_status && (
          <Badge variant={getStatusVariant(document.extraction_status)}>
            {document.extraction_status}
          </Badge>
        )}
      </div>
    </Link>
  );
}
