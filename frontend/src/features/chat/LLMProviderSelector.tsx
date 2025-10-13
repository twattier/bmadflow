import { useLLMProviders } from '@/api/hooks/useLLMProviders';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface LLMProviderSelectorProps {
  onProviderSelect: (providerId: string) => void;
  selectedProviderId?: string;
}

export function LLMProviderSelector({
  onProviderSelect,
  selectedProviderId,
}: LLMProviderSelectorProps) {
  const { data: providers, isLoading, error } = useLLMProviders();

  if (isLoading) {
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">Select LLM Provider</label>
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Failed to load LLM providers</AlertDescription>
      </Alert>
    );
  }

  if (!providers || providers.length === 0) {
    return (
      <Alert>
        <AlertDescription>
          No LLM providers configured. Go to Configuration to add one.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-2">
      <label htmlFor="llm-provider" className="text-sm font-medium">
        Select LLM Provider
      </label>
      <Select value={selectedProviderId} onValueChange={onProviderSelect}>
        <SelectTrigger id="llm-provider">
          <SelectValue placeholder="Choose an LLM provider..." />
        </SelectTrigger>
        <SelectContent>
          {providers.map((provider) => (
            <SelectItem key={provider.id} value={provider.id}>
              {provider.provider_name} - {provider.model_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
