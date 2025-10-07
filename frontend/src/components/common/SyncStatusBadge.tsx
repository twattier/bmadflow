import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import type { ProjectDocResponse } from '@/api/types/projectDoc';

interface SyncStatusBadgeProps {
  projectDoc: ProjectDocResponse;
}

function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return 'Never';

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

export function SyncStatusBadge({ projectDoc }: SyncStatusBadgeProps) {
  const { last_synced_at, last_github_commit_date } = projectDoc;

  // Determine badge state
  let badgeText: string;
  let badgeVariant: 'default' | 'secondary' | 'destructive' | 'outline';
  let showTooltip = false;

  if (last_synced_at === null) {
    badgeText = 'Not synced';
    badgeVariant = 'secondary';
  } else if (last_github_commit_date === null) {
    badgeText = '⚠ Source unavailable';
    badgeVariant = 'destructive';
    showTooltip = true;
  } else {
    const syncDate = new Date(last_synced_at);
    const commitDate = new Date(last_github_commit_date);

    if (syncDate >= commitDate) {
      badgeText = '✓ Up to date';
      badgeVariant = 'default';
    } else {
      badgeText = '⚠ Needs update';
      badgeVariant = 'outline';
    }
  }

  const relativeTime = formatRelativeTime(last_synced_at);

  const badgeElement = (
    <div className="flex flex-col gap-1">
      <Badge variant={badgeVariant} data-testid="sync-status-badge">
        {badgeText}
      </Badge>
      <span className="text-xs text-muted-foreground" data-testid="last-synced-time">
        Last synced: {relativeTime}
      </span>
    </div>
  );

  if (showTooltip) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{badgeElement}</TooltipTrigger>
          <TooltipContent>
            <p>GitHub repository not accessible. Check URL or permissions.</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return badgeElement;
}
