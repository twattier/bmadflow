import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import TabNavigation from '../../src/components/layout/TabNavigation';

describe('TabNavigation', () => {
  it('renders all 4 tabs with correct labels', () => {
    render(
      <BrowserRouter>
        <TabNavigation />
      </BrowserRouter>
    );

    expect(screen.getByText('Scoping')).toBeInTheDocument();
    expect(screen.getByText('Architecture')).toBeInTheDocument();
    expect(screen.getByText('Epics')).toBeInTheDocument();
    expect(screen.getByText('Detail')).toBeInTheDocument();
  });

  it('renders tabs with correct icons', () => {
    const { container } = render(
      <BrowserRouter>
        <TabNavigation />
      </BrowserRouter>
    );

    // Check that SVG icons are rendered (Lucide icons render as SVGs)
    const svgIcons = container.querySelectorAll('svg');
    expect(svgIcons).toHaveLength(4);
  });

  it('tabs are clickable links', () => {
    render(
      <BrowserRouter>
        <TabNavigation />
      </BrowserRouter>
    );

    const scopingTab = screen.getByText('Scoping').closest('a');
    const architectureTab = screen.getByText('Architecture').closest('a');
    const epicsTab = screen.getByText('Epics').closest('a');
    const detailTab = screen.getByText('Detail').closest('a');

    expect(scopingTab).toHaveAttribute('href', '/scoping');
    expect(architectureTab).toHaveAttribute('href', '/architecture');
    expect(epicsTab).toHaveAttribute('href', '/epics');
    expect(detailTab).toHaveAttribute('href', '/detail');
  });
});
