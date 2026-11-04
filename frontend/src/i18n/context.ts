import { createContext } from 'react';
import { en } from './en';
import type { Locale, Messages } from './index';

export type I18n = {
  locale: Locale;
  messages: Messages;
  setLocale: (locale: Locale) => void;
};

// Outside the provider, as in a component's own tests, the interface is in English
export const I18nContext = createContext<I18n>({
  locale: 'en',
  messages: en,
  setLocale: () => undefined,
});
