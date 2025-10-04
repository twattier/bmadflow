import { describe, it, expect } from 'vitest';
import { parseLinkUrl } from '@/utils/parseLinkUrl';

describe('parseLinkUrl', () => {
  describe('External links', () => {
    it('classifies http links as external', () => {
      const result = parseLinkUrl('http://github.com');
      expect(result.type).toBe('external');
      expect(result.href).toBe('http://github.com');
    });

    it('classifies https links as external', () => {
      const result = parseLinkUrl('https://github.com');
      expect(result.type).toBe('external');
      expect(result.href).toBe('https://github.com');
    });

    it('treats non-.md links as external', () => {
      const result = parseLinkUrl('/some/path/file.pdf');
      expect(result.type).toBe('external');
      expect(result.href).toBe('/some/path/file.pdf');
    });
  });

  describe('Internal markdown links', () => {
    it('classifies .md links as internal', () => {
      const result = parseLinkUrl('../architecture.md');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('../architecture.md');
      expect(result.href).toBe('../architecture.md');
    });

    it('handles relative paths with ./', () => {
      const result = parseLinkUrl('./story.md');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('./story.md');
    });

    it('handles absolute paths', () => {
      const result = parseLinkUrl('/docs/epics/epic-1.md');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('/docs/epics/epic-1.md');
    });

    it('extracts fragment from markdown link', () => {
      const result = parseLinkUrl('../epic-1.md#story-1-1');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('../epic-1.md');
      expect(result.fragment).toBe('story-1-1');
    });

    it('handles links without fragments', () => {
      const result = parseLinkUrl('../prd.md');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('../prd.md');
      expect(result.fragment).toBeUndefined();
    });
  });

  describe('Anchor links', () => {
    it('classifies # links as anchor', () => {
      const result = parseLinkUrl('#section-heading');
      expect(result.type).toBe('anchor');
      expect(result.fragment).toBe('section-heading');
      expect(result.href).toBe('#section-heading');
    });

    it('handles anchor with kebab-case', () => {
      const result = parseLinkUrl('#my-section-name');
      expect(result.type).toBe('anchor');
      expect(result.fragment).toBe('my-section-name');
    });
  });

  describe('Edge cases', () => {
    it('handles empty string', () => {
      const result = parseLinkUrl('');
      expect(result.type).toBe('external');
      expect(result.href).toBe('');
    });

    it('handles whitespace-only string', () => {
      const result = parseLinkUrl('   ');
      expect(result.type).toBe('external');
    });

    it('trims whitespace from href', () => {
      const result = parseLinkUrl('  ../doc.md  ');
      expect(result.type).toBe('internal');
      expect(result.href).toBe('../doc.md');
    });

    it('handles complex relative paths', () => {
      const result = parseLinkUrl('../../architecture/tech-stack.md');
      expect(result.type).toBe('internal');
      expect(result.filePath).toBe('../../architecture/tech-stack.md');
    });
  });
});
