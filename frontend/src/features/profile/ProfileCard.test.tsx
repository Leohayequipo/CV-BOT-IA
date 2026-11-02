import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { currentRoles, profile } from './profile';
import { ProfileCard } from './ProfileCard';

describe('ProfileCard', () => {
  it('shows who he is and that he can work in the EU', () => {
    render(<ProfileCard />);

    expect(screen.getByRole('img', { name: profile.basics.photo.alt.en })).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 1, name: profile.basics.name }),
    ).toBeInTheDocument();
    expect(screen.getByText('EU citizen, no visa needed')).toBeInTheDocument();
  });

  it('lists every role he holds today', () => {
    render(<ProfileCard />);

    const rows = within(screen.getByRole('list')).getAllByRole('listitem');
    expect(rows.map((row) => row.textContent)).toEqual(
      currentRoles.map((role) => expect.stringContaining(role.company)),
    );
  });

  it('links a current company to its site', () => {
    const company = currentRoles.find((role) => role.url !== null);

    render(<ProfileCard />);

    expect(company).toBeDefined();
    expect(screen.getByRole('link', { name: new RegExp(company?.company ?? '') })).toHaveAttribute(
      'href',
      company?.url,
    );
  });
});
