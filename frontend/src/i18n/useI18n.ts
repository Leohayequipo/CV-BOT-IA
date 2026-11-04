import { useContext } from 'react';
import { I18nContext } from './context';

/** The interface language, its copy, and the way to change it. */
export function useI18n() {
  return useContext(I18nContext);
}
