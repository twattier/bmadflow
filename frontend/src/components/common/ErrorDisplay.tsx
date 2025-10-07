import { AlertCircle } from 'lucide-react';

interface ErrorDisplayProps {
  error: Error | null;
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <AlertCircle className="h-12 w-12 text-destructive mb-4" />
      <h3 className="text-lg font-semibold mb-2">Error</h3>
      <p className="text-sm text-muted-foreground">
        {error?.message || 'An unexpected error occurred'}
      </p>
    </div>
  );
}
