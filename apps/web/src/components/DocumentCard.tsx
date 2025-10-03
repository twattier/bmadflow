import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Badge } from './ui/badge';
import { StatusBadge } from './StatusBadge';
import type { Document } from '../types/document';
import type { Epic } from '../types/epic';

interface DocumentCardProps {
  document: Document;
  epic?: Epic;
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

export function DocumentCard({ document, epic }: DocumentCardProps) {
  const storyCount = epic?.extracted_epic?.story_count ?? 0;
  const storyText = storyCount === 1 ? '1 story' : `${storyCount} stories`;

  return (
    <Link
      to={`/detail/${epic?.id || document.id}`}
      className="block p-6 border rounded-lg hover:shadow-lg transition-shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary cursor-pointer bg-card"
    >
      {/* Title */}
      <h3 className="text-lg font-semibold line-clamp-2 leading-[1.4]">
        {epic?.title || document.title}
      </h3>

      {/* Status badge + Story Count (for Epics only) */}
      {epic && (
        <div className="flex items-center gap-2 mt-2">
          <StatusBadge status={epic.extracted_epic?.status || 'draft'} />
          <span className="text-sm text-muted-foreground">{storyText}</span>
        </div>
      )}

      {/* Excerpt */}
      <p className="text-sm text-muted-foreground line-clamp-3 mt-2">
        {epic?.excerpt || document.excerpt}
      </p>

      {/* Footer with date and badge (non-epic documents) */}
      <div className="flex items-center justify-between mt-4">
        {/* Last modified date */}
        <p className="text-xs text-muted-foreground">
          {formatDistanceToNow(new Date(epic?.last_modified || document.last_modified), {
            addSuffix: true,
          })}
        </p>

        {/* Status badge for non-epic documents */}
        {!epic && document.extraction_status && (
          <Badge variant={getStatusVariant(document.extraction_status)}>
            {document.extraction_status}
          </Badge>
        )}
      </div>
    </Link>
  );
}
