import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { CoverGraph } from './CoverGraph';
import { litPath } from './graphPath';

function litParts(container: HTMLElement): string[] {
  return [...container.querySelectorAll('[data-lit="true"]')].map(
    (element) => element.getAttribute('data-part') ?? '',
  );
}

describe('CoverGraph', () => {
  it('rests while nothing is thinking', () => {
    const { container } = render(<CoverGraph />);

    expect(litParts(container)).toEqual([]);
  });

  it('lights the path up to the agent that answers', () => {
    const { container } = render(<CoverGraph activeNode="job_fit" />);

    expect(litParts(container).toSorted()).toEqual(
      [
        'guardrail',
        'guardrail-supervisor',
        'job_fit',
        'supervisor',
        'supervisor-job_fit',
      ].toSorted(),
    );
  });

  it('lights only the steps reached so far', () => {
    expect(litPath('guardrail')).toEqual({ guardrail: true, supervisor: false, agent: null });
    expect(litPath('supervisor')).toEqual({ guardrail: true, supervisor: true, agent: null });
  });
});
