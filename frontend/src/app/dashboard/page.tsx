"use client";

import { useState, useEffect } from "react";

import { motion } from "framer-motion";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from "recharts";
import { Trophy, Flag, Timer, Zap } from "lucide-react";

// Mock Data for the prototype
const fallbackStandings = [
  { driver: "VER", points: 400, wins: 15, podiums: 18 },
  { driver: "NOR", points: 310, wins: 4, podiums: 12 },
  { driver: "LEC", points: 280, wins: 2, podiums: 10 },
  { driver: "PIA", points: 240, wins: 1, podiums: 8 },
  { driver: "SAI", points: 200, wins: 1, podiums: 7 },
];

const seasonTrend = [
  { race: "BHR", VER: 25, NOR: 12, LEC: 15 },
  { race: "SAU", VER: 50, NOR: 24, LEC: 30 },
  { race: "AUS", VER: 50, NOR: 42, LEC: 55 },
  { race: "JPN", VER: 76, NOR: 50, LEC: 67 },
  { race: "CHN", VER: 101, NOR: 68, LEC: 79 },
  { race: "MIA", VER: 119, NOR: 93, LEC: 94 },
];

const driverRadar = [
  { subject: 'Consistency', VER: 98, NOR: 90, fullMark: 100 },
  { subject: 'Qualifying', VER: 95, NOR: 92, fullMark: 100 },
  { subject: 'Race Pace', VER: 100, NOR: 88, fullMark: 100 },
  { subject: 'Tire Management', VER: 90, NOR: 85, fullMark: 100 },
  { subject: 'Overtaking', VER: 85, NOR: 80, fullMark: 100 },
];

export default function Dashboard() {
  const [driverStandings, setDriverStandings] = useState(fallbackStandings);

  useEffect(() => {
    fetch("http://localhost:8001/api/data/standings")
      .then(res => res.json())
      .then(data => {
        if(Array.isArray(data)) {
          const formatted = data.map((d: any) => ({
            driver: d.name.substring(0, 3).toUpperCase(),
            points: d.points,
            wins: d.wins,
            podiums: d.podiums
          }));
          setDriverStandings(formatted);
        }
      })
      .catch(console.error);
  }, []);

  return (
    <div className="p-6 md:p-10 max-w-[1600px] mx-auto w-full">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Global Analytics Dashboard</h1>
          <p className="text-gray-400">Season overview, driver standings, and constructor performance.</p>
        </div>
        <div className="flex gap-2">
          <select className="bg-white/5 border border-white/10 rounded px-4 py-2 outline-none focus:border-f1-red text-sm">
            <option>2025 Season</option>
            <option>2024 Season</option>
          </select>
        </div>
      </div>

      {/* Top Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Championship Leader" value="M. Verstappen" subValue="400 pts" icon={<Trophy className="text-yellow-500" />} />
        <StatCard title="Constructors Leader" value="Red Bull Racing" subValue="560 pts" icon={<Flag className="text-blue-500" />} />
        <StatCard title="Fastest Pit Stop" value="1.82s" subValue="McLaren (MIA)" icon={<Timer className="text-orange-500" />} />
        <StatCard title="Most Consistent" value="L. Norris" subValue="Avg Finish: 3.2" icon={<Zap className="text-green-500" />} />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Trend Line Chart */}
        <div className="glass-panel rounded-2xl p-6 lg:col-span-2">
          <h3 className="text-lg font-bold mb-6">Championship Points Progression</h3>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={seasonTrend} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="race" stroke="#888" tick={{ fill: '#888' }} />
                <YAxis stroke="#888" tick={{ fill: '#888' }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Line type="monotone" dataKey="VER" stroke="#0019bf" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="NOR" stroke="#ff8000" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="LEC" stroke="#e10600" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="glass-panel rounded-2xl p-6">
          <h3 className="text-lg font-bold mb-6">Performance Index (VER vs NOR)</h3>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={driverRadar}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#aaa', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'transparent' }} />
                <Radar name="Verstappen" dataKey="VER" stroke="#0019bf" fill="#0019bf" fillOpacity={0.4} />
                <Radar name="Norris" dataKey="NOR" stroke="#ff8000" fill="#ff8000" fillOpacity={0.4} />
                <RechartsTooltip contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="glass-panel rounded-2xl p-6 lg:col-span-3">
          <h3 className="text-lg font-bold mb-6">Driver Standings (Points & Wins)</h3>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={driverStandings} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="driver" stroke="#888" />
                <YAxis yAxisId="left" orientation="left" stroke="#888" />
                <YAxis yAxisId="right" orientation="right" stroke="#888" />
                <RechartsTooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar yAxisId="left" dataKey="points" fill="var(--f1-red)" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="wins" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

function StatCard({ title, value, subValue, icon }: { title: string, value: string, subValue: string, icon: React.ReactNode }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 rounded-2xl relative overflow-hidden group"
    >
      <div className="absolute -right-4 -top-4 opacity-5 group-hover:scale-150 transition-transform duration-500">
        <div className="w-24 h-24">{icon}</div>
      </div>
      <div className="flex items-center gap-3 mb-4">
        <div className="bg-white/5 p-2 rounded-lg">{icon}</div>
        <h4 className="text-gray-400 font-medium text-sm uppercase tracking-wider">{title}</h4>
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm text-f1-red font-medium">{subValue}</div>
    </motion.div>
  );
}
