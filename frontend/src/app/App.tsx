import { ChatPanel } from '../features/chat/ChatPanel';
import { useChat } from '../features/chat/useChat';
import { PhoneHeader } from '../features/profile/PhoneHeader';
import { ProfileColumn } from '../features/profile/ProfileColumn';
import { ShortcutsColumn } from '../features/shortcuts/ShortcutsColumn';
import { useTheme } from '../features/theme/useTheme';
import { TopBar } from './TopBar';

/**
 * Desktop: a top bar over three columns that wrap when the window narrows (DESIGN.md).
 * Phone, below 768 px: a header with the profile, and the chat filling the rest of the screen.
 */
export function App() {
  const { theme, toggleTheme } = useTheme();
  const chat = useChat();
  return (
    <div className="flex h-dvh flex-col md:block md:h-auto md:min-h-dvh">
      <TopBar theme={theme} onToggleTheme={toggleTheme} onAsk={chat.ask} />
      <PhoneHeader theme={theme} onToggleTheme={toggleTheme} />
      <main className="mx-auto flex min-h-0 w-full max-w-[1160px] flex-1 flex-col md:flex-row md:flex-wrap md:items-start md:gap-6 md:px-4 md:pt-6 md:pb-8">
        <ProfileColumn onAsk={chat.ask} />
        <ChatPanel
          conversation={chat.messages}
          busy={chat.busy}
          limited={chat.limited}
          onAsk={chat.ask}
          onRetry={chat.retry}
          onStop={chat.stop}
          onReset={chat.reset}
        />
        <ShortcutsColumn onAsk={chat.ask} />
      </main>
    </div>
  );
}
