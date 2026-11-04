import type { Locale } from '../i18n';
import { useI18n } from '../i18n/useI18n';

const LANGUAGES: { locale: Locale; label: string; name: string }[] = [
  { locale: 'es', label: 'ES', name: 'Español' },
  { locale: 'en', label: 'EN', name: 'English' },
];

/** ES / EN in the top bar; each language names itself, as visitors look for their own. */
export function LanguageSwitch() {
  const { locale, messages, setLocale } = useI18n();
  return (
    <fieldset className="m-0 flex min-w-0 overflow-hidden rounded-full border border-border-strong p-0">
      <legend className="sr-only">{messages.language.label}</legend>
      {LANGUAGES.map((language) => {
        const current = language.locale === locale;
        return (
          <button
            key={language.locale}
            type="button"
            lang={language.locale}
            aria-label={language.name}
            aria-pressed={current}
            onClick={() => setLocale(language.locale)}
            className={`h-[38px] px-3 text-label font-semibold ${current ? 'bg-text text-card' : 'text-muted hover:bg-subtle'}`}
          >
            {language.label}
          </button>
        );
      })}
    </fieldset>
  );
}
