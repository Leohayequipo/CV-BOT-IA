/** Links that depend on deployment configuration; null when it isn't set. */

export const REPO_URL = 'https://github.com/Leohayequipo/CV-BOT-IA';

export function whatsappUrl(phone = import.meta.env.VITE_CONTACT_PHONE): string | null {
  const digits = phone?.replace(/\D/g, '');
  return digits ? `https://wa.me/${digits}` : null;
}

export function cvUrl(url = import.meta.env.VITE_CV_URL): string | null {
  return url?.trim() || null;
}
