import { Button } from './ui/button';

interface EmptyStateProps {
  title?: string;
  message?: string;
  onAction?: () => void;
  actionLabel?: string;
}

export function EmptyState({
  title = 'No scoping documents found',
  message = 'Check your repository structure. Scoping documents should be in `/docs/scoping/` directory.',
  onAction,
  actionLabel = 'Sync Repository',
}: EmptyStateProps) {
  const handleAction = () => {
    if (onAction) {
      onAction();
    } else {
      // AC6: Placeholder if Story 3.8 not complete
      // TODO: Replace with actual sync functionality when Story 3.8 is implemented
      alert('Sync feature coming soon');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
      {/* Icon - AC6 */}
      <div className="text-6xl mb-4">📄</div>

      {/* Message - AC6 */}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-md">{message}</p>

      {/* Action button - AC6 */}
      <Button onClick={handleAction} variant="outline">
        {actionLabel}
      </Button>
    </div>
  );
}
