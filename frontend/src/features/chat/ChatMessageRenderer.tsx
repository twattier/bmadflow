import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { cn } from '@/lib/utils';

interface ChatMessageRendererProps {
  content: string;
  className?: string;
}

export function ChatMessageRenderer({ content, className }: ChatMessageRendererProps) {
  return (
    <div
      className={cn(
        'prose prose-slate prose-sm max-w-none dark:prose-invert',
        'prose-headings:mb-2 prose-headings:mt-3',
        'prose-p:my-2 prose-p:leading-relaxed',
        'prose-ul:my-2 prose-ol:my-2 prose-li:my-1',
        'prose-code:bg-gray-100 prose-code:text-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono prose-code:border prose-code:border-gray-200',
        'prose-pre:bg-transparent prose-pre:p-0',
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          code(props) {
            const { children, className, node, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const inline = !node || node.position?.start.line === node.position?.end.line;

            // Handle code blocks with syntax highlighting
            if (!inline && match) {
              return (
                <SyntaxHighlighter
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  style={oneLight as any}
                  language={language}
                  PreTag="div"
                  customStyle={{
                    margin: '0.75rem 0',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                    padding: '1rem',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                  }}
                  codeTagProps={{
                    style: {
                      fontFamily:
                        'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                    },
                  }}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              );
            }

            // Inline code
            return (
              <code className={cn('text-sm', className)} {...rest}>
                {children}
              </code>
            );
          },
          a(props) {
            const { children, href, ...rest } = props;
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
                {...rest}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
