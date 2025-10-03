import { Skeleton } from '../ui/skeleton';

export default function MarkdownLoadingSkeleton() {
  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-8" data-testid="markdown-skeleton">
      {/* Title placeholder */}
      <Skeleton className="h-10 w-3/5 mb-8" />

      {/* Content placeholders */}
      <div className="space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-11/12" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-10/12" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-9/12" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-11/12" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    </div>
  );
}
