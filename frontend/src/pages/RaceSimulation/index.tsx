import { useState } from 'react';
import { PlaySquare, Navigation, Activity, TrendingUp } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const mockDistributionData = Array.from({ length: 20 }, (_, i) => {
  const pos = i + 1;
  // Create a normal-ish distribution centered around P5
  let prob = Math.exp(-Math.pow(pos - 5, 2) / 8) * 100;
  if (prob < 1) prob = Math.random() * 2; // noise
  return { position: `P${pos}`, probability: prob.toFixed(1) };
});

const mockStrategyData = Array.from({ length: 78 }, (_, i) => {
  const lap = i + 1;
  // Simulate tyre degradation curves
  const oneStop = 100 - (lap * 1.2) + (lap > 40 ? 40 : 0); // Pit lap 40
  const twoStop = 100 - (lap * 1.5) + (lap > 25 ? 50 : 0) + (lap > 55 ? 50 : 0); // Pit 25, 55
  return { lap, oneStop: Math.max(0, oneStop), twoStop: Math.max(0, twoStop) };
});

export default function RaceSimulation() {
  const [running, setRunning] = useState(false);
  const [ran, setRan] = useState(false);

  const runSimulation = () => {
    setRunning(true);
    setTimeout(() => {
      setRunning(false);
      setRan(true);
    }, 2000);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Race Simulation Center</h1>
          <p className="text-gray-400 mt-1">Advanced Monte Carlo race outcome simulations</p>
        </div>
        <button
          onClick={runSimulation}
          disabled={running}
          className="px-6 py-2 bg-f1-red hover:bg-f1-neon disabled:opacity-50 text-white font-bold rounded shadow-[0_0_15px_rgba(225,6,0,0.3)] transition-all flex items-center gap-2"
        >
          {running ? <Activity className="w-4 h-4 animate-spin" /> : <PlaySquare className="w-4 h-4" />}
          {running ? 'Simulating 10,000 Races...' : 'Run Simulation'}
        </button>
      </div>

      <div className="bg-f1-card border border-f1-border rounded-lg p-4 flex items-start gap-3">
        <Navigation className="w-5 h-5 text-f1-red mt-0.5" />
        <div>
          <p className="text-sm font-bold text-white">Preview Mode</p>
          <p className="text-xs text-gray-400">Currently displaying static premium mock data to demonstrate visualization capabilities.</p>
        </div>
      </div>

      {(!ran && !running) ? (
        <div className="glass-panel rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
          <PlaySquare className="w-16 h-16 text-gray-600 mb-4" />
          <h2 className="text-xl font-bold mb-2 text-gray-300">Ready to Simulate</h2>
          <p className="text-gray-500 max-w-md text-sm">Click "Run Simulation" to generate probability distributions across 10,000 Monte Carlo iterations.</p>
        </div>
      ) : running ? (
        <div className="glass-panel rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
          <div className="w-16 h-16 rounded-full border-4 border-f1-border border-t-f1-red animate-spin mb-4" />
          <h2 className="text-xl font-mono text-f1-neon font-bold animate-pulse">COMPUTING PROBABILITIES</h2>
          <p className="text-gray-500 max-w-md text-sm mt-2">Evaluating strategy permutations...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Position Distribution */}
          <div className="glass-panel rounded-xl p-6 flex flex-col min-h-[350px]">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-6 flex items-center gap-2">
              <Activity className="w-4 h-4 text-f1-red" />
              Finish Position Distribution (Max Verstappen)
            </h3>
            <div className="flex-1 w-full h-full relative -ml-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockDistributionData}>
                  <defs>
                    <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#e10600" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#e10600" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="position" stroke="#888d96" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888d96" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#151620', borderColor: '#23252f', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                    formatter={(value: any) => [`${value}%`, 'Probability']}
                  />
                  <Area type="monotone" dataKey="probability" stroke="#e10600" strokeWidth={2} fillOpacity={1} fill="url(#colorProb)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Strategy Comparison */}
          <div className="glass-panel rounded-xl p-6 flex flex-col min-h-[350px]">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-6 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Tyre Degradation vs Strategy (Monaco)
            </h3>
            <div className="flex-1 w-full h-full relative -ml-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockStrategyData}>
                  <XAxis dataKey="lap" stroke="#888d96" fontSize={10} tickLine={false} axisLine={false} label={{ value: 'Lap Number', position: 'insideBottom', fill: '#888d96', fontSize: 10, dy: 10 }} />
                  <YAxis stroke="#888d96" fontSize={10} tickLine={false} axisLine={false} label={{ value: 'Tyre Performance %', angle: -90, position: 'insideLeft', fill: '#888d96', fontSize: 10, dx: -10 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#151620', borderColor: '#23252f', borderRadius: '8px' }}
                  />
                  <Line type="monotone" dataKey="oneStop" name="1-Stop Strategy" stroke="#06b6d4" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="twoStop" name="2-Stop Strategy" stroke="#e10600" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center gap-4 mt-4 justify-center text-xs text-gray-400">
              <div className="flex items-center gap-2"><div className="w-3 h-0.5 bg-cyan-400"></div> 1-Stop</div>
              <div className="flex items-center gap-2"><div className="w-3 h-0.5 bg-f1-red"></div> 2-Stop</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
