import { useI18n } from '../../i18n/useI18n';

type SuggestedQuestionsProps = {
  questions: string[];
  onAsk: (question: string) => void;
  // Desktop: chips wrap under the latest answer. Phone: one row that scrolls sideways
  layout: 'wrap' | 'row';
};

export function SuggestedQuestions({ questions, onAsk, layout }: SuggestedQuestionsProps) {
  const { messages } = useI18n();
  if (questions.length === 0) return null;
  const list =
    layout === 'wrap'
      ? 'mt-3 hidden flex-wrap gap-2 md:flex'
      : 'flex gap-2 overflow-x-auto px-3.5 pt-1 pb-2.5 md:hidden';
  return (
    <ul aria-label={messages.chat.suggestionsLabel} className={list}>
      {questions.map((question) => (
        <li key={question} className="shrink-0">
          <button
            type="button"
            onClick={() => onAsk(question)}
            className={`min-h-9 rounded-full border border-accent bg-card px-3.5 py-1.5 text-left text-small font-semibold text-accent hover:bg-accent-soft ${layout === 'row' ? 'whitespace-nowrap' : ''}`}
          >
            {question}
          </button>
        </li>
      ))}
    </ul>
  );
}
