import { ChatPanel } from '../features/chat/ChatPanel';
import { useChat } from '../features/chat/useChat';
import { PhoneHeader } from '../features/profile/PhoneHeader';
import { ProfileColumn } from '../features/profile/ProfileColumn';
import { ShortcutsColumn } from '../features/shortcuts/ShortcutsColumn';
import { useTheme } from '../features/theme/useTheme';
import { useIsDesktop } from '../lib/useMediaQuery';
import { I18nProvider } from '../i18n/I18nProvider';
import { useI18n } from '../i18n/useI18n';
import { focusQuestionBox, QUESTION_BOX_ID } from '../features/chat/questionBox';
import { TopBar } from './TopBar';

/**
 * Desktop: a top bar over three columns that wrap when the window narrows (DESIGN.md).
 * Phone, below 768 px: a header with the profile, and the chat filling the rest of the screen.
 */
export function App() {
  return (
    <I18nProvider>
      <Page />
    </I18nProvider>
  );
}

function Page() {
  const { messages } = useI18n();
  const { theme, toggleTheme } = useTheme();
  const chat = useChat();
  const desktop = useIsDesktop();
  return (
    <div className="flex h-dvh flex-col md:block md:h-auto md:min-h-dvh">
      {/* Hidden until focused: the first Tab offers to skip straight to the question box */}
      <a
        href={`#${QUESTION_BOX_ID}`}
        onClick={(event) => {
          event.preventDefault();
          focusQuestionBox();
        }}
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-full focus:bg-accent focus:px-4 focus:py-2 focus:font-semibold focus:text-accent-ink"
      >
        {messages.site.skipToQuestion}
      </a>
      {desktop ? (
        <TopBar theme={theme} onToggleTheme={toggleTheme} onAsk={chat.ask} />
      ) : (
        <PhoneHeader theme={theme} onToggleTheme={toggleTheme} />
      )}
      <main className="mx-auto flex min-h-0 w-full max-w-[1160px] flex-1 flex-col md:flex-row md:flex-wrap md:items-start md:gap-6 md:px-4 md:pt-6 md:pb-8">
        {desktop && <ProfileColumn onAsk={chat.ask} activeNode={chat.graphNode} />}
        <ChatPanel
          conversation={chat.messages}
          busy={chat.busy}
          limited={chat.limited}
          onAsk={chat.ask}
          onRetry={chat.retry}
          onStop={chat.stop}
          onReset={chat.reset}
          onSendContact={chat.confirmContact}
        />
        {desktop && <ShortcutsColumn onAsk={chat.ask} />}
      </main>
    </div>
  );
}
