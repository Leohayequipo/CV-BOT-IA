import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { Citation } from '../api';
import type { JobFitCardData, ProjectCardData } from './cardData';
import { JobFitCard } from './JobFitCard';
import { ProjectCard } from './ProjectCard';

const citations: Citation[] = [
  { id: 1, label: 'UTN · AI R&D Developer', source: 'profile.yaml', section: 'experience.utn' },
];

describe('JobFitCard', () => {
  const data: JobFitCardData = {
    title: 'AI Engineer · remote in the EU',
    requirements: [
      { requirement: 'Python and FastAPI', status: 'met', evidence: 'FastAPI at UTN [1]' },
      { requirement: 'RAG', status: 'met', evidence: 'RAG document assistant [1]' },
      { requirement: 'English C1', status: 'partial', evidence: 'B1, with daily practice' },
      { requirement: 'AWS', status: 'missing', evidence: 'Not in his CV' },
    ],
  };

  it('counts the summary from its rows, so they always agree', () => {
    render(<JobFitCard data={data} citations={citations} />);

    expect(screen.getByText('Meets 2 of 4 requirements, 1 in part')).toBeInTheDocument();
  });

  it('labels each requirement, gaps included', () => {
    render(<JobFitCard data={data} citations={citations} />);

    const aws = screen.getByText('AWS').closest('li');
    expect(aws).not.toBeNull();
    expect(within(aws as HTMLElement).getByText('No evidence')).toBeInTheDocument();
    expect(within(aws as HTMLElement).getByText('Not in his CV')).toBeInTheDocument();
  });

  it('shows the citations in the evidence', () => {
    render(<JobFitCard data={data} citations={citations} />);

    expect(screen.getAllByText('Source 1: UTN · AI R&D Developer')).toHaveLength(2);
  });
});

describe('ProjectCard', () => {
  const data: ProjectCardData = {
    name: 'ServiME',
    summary: 'AI digital menu and chat SaaS for restaurants',
    role: 'Lead Developer',
    period: 'Aug 2026 – present',
    highlight: '20% faster service',
    stack: ['Laravel', 'React'],
    url: 'https://servime.net/',
    brand: 'servime',
  };

  it("uses the project's own colours only when DESIGN.md defines them", () => {
    const { container, rerender } = render(<ProjectCard data={data} citations={[]} />);
    expect(container.firstElementChild).toHaveClass('brand-servime');

    rerender(<ProjectCard data={{ ...data, brand: 'unknown' }} citations={[]} />);
    expect(container.firstElementChild).not.toHaveClass('brand-unknown');
  });

  it('links to the product by its host name', () => {
    render(<ProjectCard data={data} citations={[]} />);

    expect(screen.getByRole('link', { name: /servime\.net/ })).toHaveAttribute(
      'href',
      'https://servime.net/',
    );
  });
});
