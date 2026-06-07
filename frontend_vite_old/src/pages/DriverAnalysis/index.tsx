import { Users, Navigation, Trophy } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

const mockDriverData = [
  { metric: 'Qualifying Pace', driverA: 98, driverB: 92 },
  { metric: 'Race Craft', driverA: 95, driverB: 96 },
  { metric: 'Tyre Management', driverA: 90, driverB: 85 },
  { metric: 'Wet Weather', driverA: 96, driverB: 88 },
  { metric: 'Consistency', driverA: 97, driverB: 89 },
];

export default function DriverAnalysis() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Driver Analysis</h1>
        <p className="text-gray-400 mt-1">Compare driver performance metrics and historical data</p>
      </div>

      <div className="bg-f1-card border border-f1-border rounded-lg p-4 flex items-start gap-3">
        <Navigation className="w-5 h-5 text-f1-red mt-0.5" />
        <div>
          <p className="text-sm font-bold text-white">Preview Mode</p>
          <p className="text-xs text-gray-400">Currently displaying simulated premium data. Live F1 driver telemetry updates will be available once the backend endpoints are deployed.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Comparison Chart */}
        <div className="glass-panel rounded-xl p-6 flex flex-col min-h-[450px]">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-6">
            <Users className="w-5 h-5 text-f1-red" />
            Head-to-Head Attributes
          </h2>
          
          <div className="flex-1 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={mockDriverData}>
                <PolarGrid stroke="#23252f" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#888d96', fontSize: 12, fontFamily: 'monospace' }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#151620', borderColor: '#23252f', borderRadius: '8px', color: '#fff' }}
                />
                <Legend verticalAlign="top" wrapperStyle={{ fontSize: '12px', color: '#888d96', paddingBottom: '20px' }} />
                <Radar name="Max Verstappen" dataKey="driverA" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.3} />
                <Radar name="Charles Leclerc" dataKey="driverB" stroke="#e10600" fill="#e10600" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Driver Stats Cards */}
        <div className="space-y-6">
          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-cyan-400 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <Trophy className="w-24 h-24 text-cyan-400" />
            </div>
            <h3 className="text-2xl font-black font-mono tracking-tighter">MAX VERSTAPPEN</h3>
            <p className="text-xs text-gray-500 uppercase tracking-widest mb-4">Red Bull Racing</p>
            
            <div className="grid grid-cols-2 gap-4 font-mono text-sm">
              <div>
                <p className="text-gray-500 text-xs">Championships</p>
                <p className="text-white font-bold text-lg">3</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Win Rate</p>
                <p className="text-white font-bold text-lg">31.4%</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Poles</p>
                <p className="text-white font-bold text-lg">35</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Podiums</p>
                <p className="text-white font-bold text-lg">100+</p>
              </div>
            </div>
          </div>

          <div className="glass-panel rounded-xl p-6 border-l-4 border-l-f1-red relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
              <Trophy className="w-24 h-24 text-f1-red" />
            </div>
            <h3 className="text-2xl font-black font-mono tracking-tighter">CHARLES LECLERC</h3>
            <p className="text-xs text-gray-500 uppercase tracking-widest mb-4">Ferrari</p>
            
            <div className="grid grid-cols-2 gap-4 font-mono text-sm">
              <div>
                <p className="text-gray-500 text-xs">Championships</p>
                <p className="text-white font-bold text-lg">0</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Win Rate</p>
                <p className="text-white font-bold text-lg">4.5%</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Poles</p>
                <p className="text-white font-bold text-lg">23</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs">Podiums</p>
                <p className="text-white font-bold text-lg">32</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
