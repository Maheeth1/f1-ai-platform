import { Map, Wind, CloudRain, Thermometer, Navigation } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

const mockCircuitData = [
  { metric: 'Top Speed', score: 85 },
  { metric: 'Downforce', score: 95 },
  { metric: 'Tyre Wear', score: 40 },
  { metric: 'Braking', score: 70 },
  { metric: 'Overtaking', score: 30 },
];

export default function CircuitIntelligence() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Interactive Circuit Intelligence</h1>
        <p className="text-gray-400 mt-1">Analyze track characteristics and historical weather impacts</p>
      </div>

      {/* Notice about Mock Data */}
      <div className="bg-f1-card border border-f1-border rounded-lg p-4 flex items-start gap-3">
        <Navigation className="w-5 h-5 text-f1-red mt-0.5" />
        <div>
          <p className="text-sm font-bold text-white">Preview Mode</p>
          <p className="text-xs text-gray-400">Currently displaying simulated premium data. Live F1 telemetry and circuit updates will be available once the backend endpoints are deployed.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <section className="lg:col-span-4 space-y-6">
          <div className="glass-panel p-6 rounded-xl relative overflow-hidden group glass-panel-hover">
            <div className="absolute top-0 right-0 w-32 h-32 bg-f1-red/5 rounded-bl-full pointer-events-none"></div>
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-black font-mono tracking-tighter">MONACO</h2>
                <p className="text-xs text-f1-gray tracking-widest uppercase">Circuit de Monaco</p>
              </div>
              <Map className="w-8 h-8 text-f1-red opacity-80" />
            </div>

            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between pb-2 border-b border-f1-border">
                <span className="text-gray-500">Track Length</span>
                <span className="text-white font-bold">3.337 km</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-f1-border">
                <span className="text-gray-500">Laps</span>
                <span className="text-white font-bold">78</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-f1-border">
                <span className="text-gray-500">Lap Record</span>
                <span className="text-f1-neon font-bold">1:12.909</span>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-xl">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 flex items-center gap-2">
              <CloudRain className="w-4 h-4 text-cyan-400" />
              Live Weather Simulation
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-f1-dark/50 p-3 rounded-lg border border-f1-border">
                <Thermometer className="w-4 h-4 text-f1-red mb-2" />
                <p className="text-xs text-gray-500 font-mono">Track Temp</p>
                <p className="text-lg font-bold">42°C</p>
              </div>
              <div className="bg-f1-dark/50 p-3 rounded-lg border border-f1-border">
                <Wind className="w-4 h-4 text-cyan-400 mb-2" />
                <p className="text-xs text-gray-500 font-mono">Wind Speed</p>
                <p className="text-lg font-bold">12 km/h</p>
              </div>
            </div>
          </div>
        </section>

        <section className="lg:col-span-8">
          <div className="glass-panel rounded-xl p-6 h-full min-h-[400px] flex flex-col">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-6 flex items-center gap-2">
              <Map className="w-4 h-4 text-f1-red" />
              Aerodynamic & Circuit Profile
            </h3>
            <div className="flex-1 w-full relative">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={mockCircuitData}>
                  <PolarGrid stroke="#23252f" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: '#888d96', fontSize: 12, fontFamily: 'monospace' }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#151620', borderColor: '#23252f', borderRadius: '8px', color: '#fff' }}
                    itemStyle={{ color: '#ff2a24', fontWeight: 'bold' }}
                  />
                  <Radar name="Monaco" dataKey="score" stroke="#e10600" fill="#e10600" fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
