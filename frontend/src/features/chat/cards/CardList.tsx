import type { Citation } from '../api';
import type { Card } from './cardData';
import { JobFitCard } from './JobFitCard';
import { ProjectCard } from './ProjectCard';
import { SkillsCard } from './SkillsCard';
import { TimelineCard } from './TimelineCard';

/**
 * The cards of one answer. Message loads this module only when an answer has cards, so the
 * first page load doesn't carry them (frontend standards).
 */
export default function CardList({ cards, citations }: { cards: Card[]; citations: Citation[] }) {
  return cards.map((card, index) => {
    switch (card.type) {
      case 'project':
        return <ProjectCard key={index} data={card.data} citations={citations} />;
      case 'timeline':
        return <TimelineCard key={index} data={card.data} />;
      case 'skills':
        return <SkillsCard key={index} data={card.data} />;
      case 'job_fit':
        return <JobFitCard key={index} data={card.data} citations={citations} />;
      case 'contact_summary':
        // Not drawn yet: the contact flow and its confirmation complete step 4.6
        return null;
    }
  });
}
