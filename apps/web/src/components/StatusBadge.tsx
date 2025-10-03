import { Badge } from "./ui/badge";
import type { EpicStatus } from "../types/epic";

interface StatusBadgeProps {
  status: EpicStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variantMap: Record<EpicStatus, 'secondary' | 'info' | 'success'> = {
    draft: 'secondary',  // Gray
    dev: 'info',         // Blue
    done: 'success',     // Green
  };

  const displayText = status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <Badge variant={variantMap[status]}>
      {displayText}
    </Badge>
  );
}
