import { describe, expect, it } from 'vitest';
import { toCard } from './cardData';

const project = {
  name: 'ServiME',
  summary: 'AI digital menu and chat SaaS for restaurants',
  role: 'Lead Developer',
  period: 'Aug 2026 – present',
  highlight: 'In production at Azopardo Café Bar [1]',
  stack: ['Laravel', 'React'],
  url: 'https://servime.net/',
  brand: 'servime',
};

describe('toCard', () => {
  it('reads a card that follows the contract', () => {
    expect(toCard('project', project)).toEqual({ type: 'project', data: project });
  });

  it('accepts a project without a link or brand', () => {
    expect(toCard('project', { ...project, url: null, brand: null })).not.toBeNull();
  });

  it('drops a project whose link is not http or https', () => {
    expect(toCard('project', { ...project, url: 'javascript:alert(1)' })).toBeNull();
  });

  it('drops a job-fit row with an unknown status', () => {
    const data = {
      title: 'AI Engineer',
      requirements: [{ requirement: 'AWS', status: 'maybe', evidence: 'Not in his CV' }],
    };

    expect(toCard('job_fit', data)).toBeNull();
  });

  it('drops a card with missing fields or an unknown type', () => {
    expect(toCard('timeline', { items: [{ role: 'Lead Developer' }] })).toBeNull();
    expect(toCard('carousel', {})).toBeNull();
  });
});
