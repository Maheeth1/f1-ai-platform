
import { PlaySquare } from 'lucide-react';

export default function RaceSimulation() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Race Simulation</h1>
        <p className="text-gray-400 mt-1">Run full multi-lap race simulations</p>
      </div>
      <div className="glass-panel rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
        <PlaySquare className="w-16 h-16 text-gray-600 mb-4" />
        <h2 className="text-xl font-bold mb-2">Coming Soon</h2>
        <p className="text-gray-400 max-w-md">The full Race Simulation module is currently under development.</p>
      </div>
    </div>
  );
}
