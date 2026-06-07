import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import { Search, Moon, Sun, Settings, LayoutDashboard, Timer, Grid, PlaySquare, Cpu } from 'lucide-react';
import { usePreferences } from '../../store/preferences';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme } = usePreferences();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-[15vh]">
      <Command 
        className="w-full max-w-xl bg-f1-card border border-f1-border rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        onKeyDown={(e) => {
          if (e.key === 'Escape') setOpen(false);
        }}
      >
        <div className="flex items-center border-b border-f1-border px-4 py-3 gap-3 text-gray-400">
          <Search className="w-5 h-5" />
          <Command.Input 
            autoFocus 
            placeholder="Type a command or search..." 
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 font-sans"
          />
        </div>

        <Command.List className="max-h-[300px] overflow-y-auto p-2 scrollbar-none">
          <Command.Empty className="py-6 text-center text-sm text-gray-500 font-mono">No results found.</Command.Empty>

          <Command.Group heading={<span className="px-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono">Navigation</span>}>
            <Command.Item onSelect={() => runCommand(() => navigate('/'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <LayoutDashboard className="w-4 h-4" /> Dashboard
            </Command.Item>
            <Command.Item onSelect={() => runCommand(() => navigate('/lap-time'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <Timer className="w-4 h-4" /> Lap Time Predictor
            </Command.Item>
            <Command.Item onSelect={() => runCommand(() => navigate('/simulation'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <PlaySquare className="w-4 h-4" /> Race Simulation
            </Command.Item>
            <Command.Item onSelect={() => runCommand(() => navigate('/circuits'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <Grid className="w-4 h-4" /> Circuit Intelligence
            </Command.Item>
            <Command.Item onSelect={() => runCommand(() => navigate('/insights'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <Cpu className="w-4 h-4" /> AI Insights
            </Command.Item>
          </Command.Group>

          <Command.Group heading={<span className="px-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono mt-2 block">Settings</span>}>
            <Command.Item onSelect={() => runCommand(toggleTheme)} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />} Toggle Theme
            </Command.Item>
            <Command.Item onSelect={() => runCommand(() => navigate('/settings'))} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 aria-selected:bg-f1-border aria-selected:text-white cursor-pointer transition-colors">
              <Settings className="w-4 h-4" /> Preferences
            </Command.Item>
          </Command.Group>
        </Command.List>
      </Command>

      {/* Click outside to close (handled by an invisible overlay in cmdk usually, but we implement manual click handler) */}
      <div className="absolute inset-0 z-[-1]" onClick={() => setOpen(false)} />
    </div>
  );
}
