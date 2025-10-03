import { Skeleton } from './ui/skeleton';

export function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-8 max-w-7xl mx-auto">
      {/* AC5: Show 6 skeleton cards */}
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="p-6 border rounded-lg bg-card"
          data-skeleton
        >
          {/* Title placeholder - 2 lines, 80% width - AC5 */}
          <Skeleton className="h-5 w-4/5 mb-2" />
          <Skeleton className="h-5 w-3/5" />

          {/* Excerpt placeholder - 3 lines, 100% width - AC5 */}
          <div className="mt-4 space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>

          {/* Date placeholder - 1 line, 40% width - AC5 */}
          <div className="mt-4">
            <Skeleton className="h-3 w-2/5" />
          </div>
        </div>
      ))}
    </div>
  );
}
