import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  Timer, 
  Grid, 
  PlaySquare, 
  Users, 
  Cpu, 
  Settings as SettingsIcon,
  Map,
  Menu,
  X,
  Search
} from 'lucide-react';
import { useHealthCheck } from '../../hooks/useApi';
import { CommandPalette } from '../ui/CommandPalette';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/lap-time', label: 'Lap Time', icon: Timer },
  { path: '/grid', label: 'Grid Position', icon: Grid },
  { path: '/simulation', label: 'Race Sim', icon: PlaySquare },
  { path: '/circuits', label: 'Circuits', icon: Map },
  { path: '/drivers', label: 'Drivers', icon: Users },
  { path: '/insights', label: 'Insights', icon: Cpu },
  { path: '/settings', label: 'Settings', icon: SettingsIcon },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { data: health, isError } = useHealthCheck();

  const getStatusColor = () => {
    if (isError || health?.status !== 'healthy') return 'bg-f1-red shadow-[0_0_10px_rgba(225,6,0,0.5)]';
    if (!health?.model_loaded) return 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]';
    return 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]';
  };

  return (
    <div className="min-h-screen bg-f1-dark text-white carbon-grid flex flex-col md:flex-row font-sans">
      <CommandPalette />
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 border-b border-f1-border bg-f1-dark/80 backdrop-blur z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-f1-red flex items-center justify-center font-black text-sm">F1</div>
          <span className="font-bold tracking-wider">AI PLATFORM</span>
        </div>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <nav className={`
        fixed md:static inset-y-0 left-0 z-40 w-64 bg-f1-card/80 backdrop-blur border-r border-f1-border transform transition-transform duration-300 ease-in-out flex flex-col
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="hidden md:flex items-center gap-3 p-6 border-b border-f1-border">
          <div className="w-10 h-10 rounded bg-f1-red flex items-center justify-center font-black text-xl text-white shadow-[0_0_15px_rgba(225,6,0,0.3)]">F1</div>
          <div>
            <h1 className="text-lg font-bold tracking-wider leading-tight">AI PLATFORM</h1>
            <p className="text-[10px] text-f1-gray uppercase tracking-widest">Race Engine</p>
          </div>
        </div>

        <div className="p-4 border-b border-f1-border hidden md:block">
          <button 
            className="w-full flex items-center justify-between px-3 py-2 bg-f1-dark rounded-lg border border-f1-border text-gray-400 hover:text-white hover:border-f1-gray transition-colors text-sm"
            onClick={() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }))}
          >
            <span className="flex items-center gap-2"><Search className="w-4 h-4" /> Search</span>
            <kbd className="hidden sm:inline-block font-mono text-[10px] bg-f1-border px-1.5 py-0.5 rounded text-gray-500">⌘K</kbd>
          </button>
        </div>

        <div className="flex-1 py-6 flex flex-col gap-2 px-4 overflow-y-auto">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium
                ${isActive 
                  ? 'bg-f1-red/10 text-white border border-f1-red/30 shadow-[inset_0_0_20px_rgba(225,6,0,0.05)] pulse-neon-border' 
                  : 'text-gray-400 hover:bg-f1-border/50 hover:text-gray-200 border border-transparent'}
              `}
            >
              <Icon className={`w-5 h-5 ${location.pathname === path ? 'text-f1-red' : ''}`} />
              {label}
            </NavLink>
          ))}
        </div>

        <div className="p-6 border-t border-f1-border">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-f1-dark/50 border border-f1-border">
            <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor()}`} />
            <div className="flex flex-col">
              <span className="text-xs font-bold text-gray-300">
                {isError || health?.status !== 'healthy' ? 'System Offline' : 'System Online'}
              </span>
              <span className="text-[10px] text-gray-500 font-mono">
                {health?.model_loaded ? 'Models Loaded' : 'No Active Model'}
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-hidden flex flex-col h-[100vh]">
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full max-w-7xl mx-auto"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Overlay for mobile menu */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </div>
  );
}
