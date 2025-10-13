import { useEffect, useState } from 'react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { useDocument } from '@/api/hooks/useDocument';
import { MarkdownRenderer } from '@/features/explorer/MarkdownRenderer';
import { useToast } from '@/hooks/use-toast';
import type { SourceDocument } from '@/api/types/message';
import { Loader2, ExternalLink, ChevronLeft } from 'lucide-react';

interface SourcePanelProps {
  source: SourceDocument | null;
  onClose: () => void;
  onOpenInExplorer: (filePath: string) => void;
  previousSource?: SourceDocument | null;
  onNavigateToPrevious?: () => void;
}

export function SourcePanel({
  source,
  onClose,
  onOpenInExplorer,
  previousSource,
  onNavigateToPrevious,
}: SourcePanelProps) {
  const { toast } = useToast();
  const [hasScrolled, setHasScrolled] = useState(false);

  // Fetch document content
  const { data: document, isLoading, error } = useDocument(source?.document_id || null);

  // Handle anchor scrolling when document loads or anchor changes
  useEffect(() => {
    if (!document || !source || hasScrolled) return;
    if (typeof window === 'undefined') return; // Skip in SSR/test environments

    // Small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      if (source.header_anchor && typeof globalThis.document !== 'undefined') {
        const element = globalThis.document.getElementById(source.header_anchor);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
          element.classList.add('highlight-fade');
          setTimeout(() => element.classList.remove('highlight-fade'), 2000);
        } else {
          // Anchor not found, show toast and scroll to top
          toast({
            description: 'Navigated to document root (section anchor unavailable)',
          });
          if (typeof window !== 'undefined' && window.scrollTo) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }
      } else if (!source.header_anchor) {
        // No anchor, show toast
        toast({
          description: 'Navigated to document root (section anchor unavailable)',
        });
      }
      setHasScrolled(true);
    }, 100);

    return () => clearTimeout(timer);
  }, [document, source, hasScrolled, toast]);

  // Reset scroll state when source changes
  useEffect(() => {
    setHasScrolled(false);
  }, [source?.document_id]);

  if (!source) return null;

  return (
    <Sheet open={!!source} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full sm:w-2/5 sm:max-w-2xl flex flex-col p-0">
        <SheetHeader className="p-4 border-b">
          <div className="flex items-center justify-between gap-2">
            {previousSource && onNavigateToPrevious && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onNavigateToPrevious}
                className="flex items-center gap-1"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
            )}
            <SheetTitle className="flex-1 text-sm truncate">{source.file_path}</SheetTitle>
            <SheetClose />
          </div>
          <SheetDescription className="sr-only">
            Document source panel displaying content from {source.file_path}
            {source.header_anchor && ` at section ${source.header_anchor}`}
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-auto p-4">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <p className="font-semibold">Failed to load document</p>
                <p className="text-sm mt-1">Please try again later</p>
              </div>
            </div>
          )}

          {document && (
            <MarkdownRenderer
              content={document.content}
              className="prose-sm"
            />
          )}
        </div>

        <SheetFooter className="p-4 border-t">
          <Button
            onClick={() => onOpenInExplorer(source.file_path)}
            className="w-full sm:w-auto"
            variant="default"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Open in Explorer
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
