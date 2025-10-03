import { useEffect, useRef, useState } from 'react';
import { Copy, Check } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism.css'; // Light theme
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-markdown';
import './codeblock.css';

interface CodeBlockProps {
  children: string;
  className?: string;
  language?: string;
}

export default function CodeBlock({ children, className, language }: CodeBlockProps) {
  const codeRef = useRef<HTMLElement>(null);
  const [copied, setCopied] = useState(false);
  const [copyFallback, setCopyFallback] = useState(false);

  // Extract language from className (format: language-typescript)
  const lang = language || className?.replace(/language-/, '') || 'text';

  useEffect(() => {
    if (codeRef.current && lang !== 'text') {
      Prism.highlightElement(codeRef.current);
    }
  }, [children, lang]);

  const handleCopy = async () => {
    const code = children.trim();

    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
        setCopyFallback(true);
        setTimeout(() => setCopyFallback(false), 3000);
      }
    } else {
      // Fallback for browsers without clipboard API
      setCopyFallback(true);
      setTimeout(() => setCopyFallback(false), 3000);
    }
  };

  return (
    <div className="relative group my-6">
      {/* Language label */}
      {lang !== 'text' && (
        <div className="code-lang-label">
          {lang}
        </div>
      )}

      {/* Copy button */}
      <button
        onClick={handleCopy}
        className="code-copy-btn"
        aria-label="Copy code"
        title={copyFallback ? 'Press Ctrl+C to copy' : 'Copy code'}
      >
        {copied ? (
          <>
            <Check className="w-4 h-4" style={{ color: '#10b981' }} />
            <span className="sr-only">Copied!</span>
          </>
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </button>

      {copyFallback && (
        <div className="code-fallback-msg">
          Press Ctrl+C to copy
        </div>
      )}

      <pre className="code-block-pre">
        <code
          ref={codeRef}
          className={lang !== 'text' ? `language-${lang}` : ''}
        >
          {children.trim()}
        </code>
      </pre>
    </div>
  );
}
