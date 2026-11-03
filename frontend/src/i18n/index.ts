import { en } from './en';

export type Locale = 'en' | 'es';

// English only until step 4.8 adds Spanish and follows the browser
export const locale: Locale = 'en';
export const messages = en;
