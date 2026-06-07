import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PreferencesState {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
  reducedMotion: boolean;
  toggleReducedMotion: () => void;
}

export const usePreferences = create<PreferencesState>()(
  persist(
    (set) => ({
      theme: 'dark',
      toggleTheme: () => set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
      reducedMotion: false,
      toggleReducedMotion: () => set((state) => ({ reducedMotion: !state.reducedMotion })),
    }),
    {
      name: 'f1-platform-preferences',
    }
  )
);
