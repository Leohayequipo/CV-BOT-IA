import { Pill } from '../../../components/ui/Pill';
import { messages } from '../../../i18n';
import { CardFrame } from './CardFrame';
import { rowEntrance } from './rowEntrance';
import type { SkillsCardData } from './cardData';

export function SkillsCard({ data }: { data: SkillsCardData }) {
  return (
    <CardFrame className="flex flex-col gap-3 px-4 py-3.5">
      <h3 className="text-card-title font-semibold">{messages.cards.mainStack}</h3>
      {data.groups.map((group, index) => (
        <div
          key={group.label}
          className={rowEntrance(index).className}
          style={rowEntrance(index).style}
        >
          <h4 className="mb-1.5 text-label font-semibold text-muted">{group.label}</h4>
          <ul className="flex flex-wrap gap-1.5">
            {group.items.map((item) => (
              <Pill key={item}>{item}</Pill>
            ))}
          </ul>
        </div>
      ))}
    </CardFrame>
  );
}
