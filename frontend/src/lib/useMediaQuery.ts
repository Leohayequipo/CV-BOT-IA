import { useSyncExternalStore } from 'react';

/** Whether a CSS media query matches now, updated when it starts or stops matching. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => {
      const list = matchMedia(query);
      list.addEventListener('change', onChange);
      return () => list.removeEventListener('change', onChange);
    },
    () => matchMedia(query).matches,
  );
}

// Tailwind's md breakpoint, where the phone layout ends (DESIGN.md)
export const DESKTOP = '(min-width: 768px)';

/**
 * Whether the desktop layout applies. The page draws only the layout that fits the screen,
 * which halves the work a phone does on load (roadmap step 4.12).
 */
export function useIsDesktop(): boolean {
  return useMediaQuery(DESKTOP);
}
