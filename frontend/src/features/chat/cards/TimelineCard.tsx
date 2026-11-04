import { InitialsTile } from '../../../components/ui/InitialsTile';
import { useI18n } from '../../../i18n/useI18n';
import { CardFrame } from './CardFrame';
import { rowEntrance } from './rowEntrance';
import type { TimelineCardData } from './cardData';

export function TimelineCard({ data }: { data: TimelineCardData }) {
  const { messages } = useI18n();
  return (
    <CardFrame className="px-4 py-3.5">
      <h3 className="mb-3 text-card-title font-semibold">{messages.cards.experience}</h3>
      <ol className="flex flex-col gap-3">
        {data.items.map((item, index) => (
          <li
            key={`${item.company}-${item.period}`}
            className={`flex gap-3 ${rowEntrance(index).className}`}
            style={rowEntrance(index).style}
          >
            <InitialsTile initials={item.initials} size="sm" />
            <div className="min-w-0">
              <p className="font-semibold">{item.role}</p>
              <p className="text-small">{item.company}</p>
              <p className="text-label text-muted">{item.period}</p>
            </div>
          </li>
        ))}
      </ol>
    </CardFrame>
  );
}
