import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SyncStatusBadge } from '@/components/common/SyncStatusBadge';
import { ProjectDocResponse } from '@/api/types/projectDoc';

describe('SyncStatusBadge', () => {
  const baseProjectDoc: ProjectDocResponse = {
    id: '123',
    project_id: 'proj-1',
    name: 'Test Docs',
    description: 'Test description',
    github_url: 'https://github.com/test/repo',
    github_folder_path: null,
    created_at: '2025-10-01T00:00:00Z',
    updated_at: '2025-10-01T00:00:00Z',
    last_synced_at: null,
    last_github_commit_date: null,
  };

  it('displays "Not synced" badge when last_synced_at is null', () => {
    render(<SyncStatusBadge projectDoc={baseProjectDoc} />);

    const badge = screen.getByTestId('sync-status-badge');
    expect(badge).toHaveTextContent('Not synced');
  });

  it('displays "Up to date" badge when last_synced_at >= last_github_commit_date', () => {
    const projectDoc: ProjectDocResponse = {
      ...baseProjectDoc,
      last_synced_at: '2025-10-07T12:00:00Z',
      last_github_commit_date: '2025-10-07T10:00:00Z',
    };

    render(<SyncStatusBadge projectDoc={projectDoc} />);

    const badge = screen.getByTestId('sync-status-badge');
    expect(badge).toHaveTextContent('✓ Up to date');
  });

  it('displays "Needs update" badge when last_synced_at < last_github_commit_date', () => {
    const projectDoc: ProjectDocResponse = {
      ...baseProjectDoc,
      last_synced_at: '2025-10-07T10:00:00Z',
      last_github_commit_date: '2025-10-07T12:00:00Z',
    };

    render(<SyncStatusBadge projectDoc={projectDoc} />);

    const badge = screen.getByTestId('sync-status-badge');
    expect(badge).toHaveTextContent('⚠ Needs update');
  });

  it('displays "Source unavailable" badge when last_github_commit_date is null but synced', () => {
    const projectDoc: ProjectDocResponse = {
      ...baseProjectDoc,
      last_synced_at: '2025-10-07T10:00:00Z',
      last_github_commit_date: null,
    };

    render(<SyncStatusBadge projectDoc={projectDoc} />);

    const badge = screen.getByTestId('sync-status-badge');
    expect(badge).toHaveTextContent('⚠ Source unavailable');
  });

  it('displays relative time correctly', () => {
    const projectDoc: ProjectDocResponse = {
      ...baseProjectDoc,
      last_synced_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      last_github_commit_date: '2025-10-07T10:00:00Z',
    };

    render(<SyncStatusBadge projectDoc={projectDoc} />);

    const timeDisplay = screen.getByTestId('last-synced-time');
    expect(timeDisplay).toHaveTextContent(/1 hour ago/);
  });

  it('displays "Never" when last_synced_at is null', () => {
    render(<SyncStatusBadge projectDoc={baseProjectDoc} />);

    const timeDisplay = screen.getByTestId('last-synced-time');
    expect(timeDisplay).toHaveTextContent('Never');
  });
});
