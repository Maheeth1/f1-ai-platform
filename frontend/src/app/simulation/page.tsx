"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ReferenceArea 
} from "recharts";
import { Settings, Droplets, ShieldAlert, Car, Play, RefreshCw, Cpu } from "lucide-react";

// Initial tire wear mock data
const generateWearData = (stints: any[], safetyCars: any[] = []) => {
  let data = [];
  let currentLap = 1;
  
  for (let s = 0; s < stints.length; s++) {
    const stint = stints[s];
    const endLap = stint.endLap;
    let wear = 100;
    
    // Different compounds wear at different rates
    const wearRate = stint.compound === "Soft" ? 2.5 : stint.compound === "Medium" ? 1.5 : 0.8;
    
    for (let lap = currentLap; lap <= endLap; lap++) {
      // SC reduces wear
      const isSC = safetyCars.some(sc => lap >= sc.start && lap <= sc.end);
      const actualWearRate = isSC ? wearRate * 0.3 : wearRate;
      
      wear = Math.max(0, wear - actualWearRate);
      data.push({
        lap,
        wear: Number(wear.toFixed(1)),
        compound: stint.compound
      });
    }
    currentLap = endLap + 1;
  }
  return data;
};

export default function Simulation() {
  const [stints, setStints] = useState([
    { id: 1, compound: "Soft", endLap: 18 },
    { id: 2, compound: "Medium", endLap: 78 } // Monaco length
  ]);
  
  const [events, setEvents] = useState([
    { id: 1, type: "SC", start: 35, end: 40, active: false },
    { id: 2, type: "Rain", start: 50, end: 78, active: false }
  ]);

  const [isSimulating, setIsSimulating] = useState(false);
  const [simResults, setSimResults] = useState<{ time: string, pos: number, risk: string } | null>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await fetch("http://localhost:8001/simulation/monte-carlo?iterations=100", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Driver: "VER",
          LapNumber: stints[stints.length - 1].endLap || 50,
          TyreLife: 10,
          Compound: stints[0].compound
        })
      });
      
      // We might get an error if DB isn't seeded but we can fallback
      let data = { mean_time: 5400 };
      if (res.ok) {
        data = await res.json();
      }

      let baseTime = data.mean_time || 5400; // 1h 30m in seconds
      if (events[0].active) baseTime += 120; // SC adds time
      if (events[1].active) baseTime += 300; // Rain adds time
      
      const hours = Math.floor(baseTime / 3600);
      const minutes = Math.floor((baseTime % 3600) / 60);
      const seconds = Math.floor(baseTime % 60);
      
      setSimResults({
        time: `${hours}h ${minutes}m ${seconds}s`,
        pos: events[1].active && stints[stints.length-1].compound !== "Inter" ? 8 : 1,
        risk: events[1].active && stints[stints.length-1].compound !== "Inter" ? "HIGH (Wrong compound)" : "LOW"
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  const activeSC = events.filter(e => e.active && e.type === "SC");
  const wearData = generateWearData(stints, activeSC);

  return (
    <div className="flex flex-col flex-1 p-6 md:p-10 max-w-[1600px] mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Race Strategy Simulator</h1>
        <p className="text-gray-400">Monte Carlo simulation engine for pit windows and what-if scenarios.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column: Controls */}
        <div className="flex flex-col gap-6 xl:col-span-1">
          
          {/* Strategy Builder */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Settings className="text-f1-red" size={20} /> Pit Strategy
            </h3>
            
            <div className="space-y-4">
              {stints.map((stint, idx) => (
                <div key={stint.id} className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="flex justify-between items-center mb-3">
                    <span className="font-bold text-sm uppercase text-gray-400">Stint {idx + 1}</span>
                    <select 
                      value={stint.compound}
                      onChange={(e) => {
                        const newStints = [...stints];
                        newStints[idx].compound = e.target.value;
                        setStints(newStints);
                      }}
                      className="bg-transparent text-white font-bold outline-none cursor-pointer"
                    >
                      <option className="bg-gray-900 text-red-500">Soft</option>
                      <option className="bg-gray-900 text-yellow-500">Medium</option>
                      <option className="bg-gray-900 text-white">Hard</option>
                      <option className="bg-gray-900 text-green-500">Inter</option>
                    </select>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Target Pit Lap</span>
                    <input 
                      type="number" 
                      value={Number.isNaN(stint.endLap) ? "" : stint.endLap} 
                      onChange={(e) => {
                        const newStints = [...stints];
                        const val = parseInt(e.target.value);
                        newStints[idx].endLap = Number.isNaN(val) ? 0 : val;
                        setStints(newStints);
                      }}
                      className="w-16 bg-white/10 rounded px-2 py-1 text-right outline-none focus:ring-1 focus:ring-f1-red"
                    />
                  </div>
                </div>
              ))}
            </div>
            
            <button className="w-full mt-4 py-3 bg-white/5 hover:bg-white/10 rounded-xl text-sm font-bold transition-colors border border-white/10 border-dashed">
              + Add Pit Stop
            </button>
          </div>

          {/* What-If Scenarios */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Cpu className="text-blue-500" size={20} /> What-If Engine
            </h3>
            
            <div className="space-y-3">
              {events.map((event, idx) => (
                <div 
                  key={event.id}
                  onClick={() => {
                    const newEvents = [...events];
                    newEvents[idx].active = !newEvents[idx].active;
                    setEvents(newEvents);
                  }}
                  className={`p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                    event.active 
                      ? "bg-blue-500/10 border-blue-500" 
                      : "bg-white/5 border-white/5 hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {event.type === "Rain" ? <Droplets size={18} className="text-blue-400" /> : <ShieldAlert size={18} className="text-yellow-500" />}
                    <span className="font-bold">{event.type}</span>
                  </div>
                  <span className="text-sm text-gray-400">Laps {event.start}-{event.end}</span>
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={handleSimulate}
            disabled={isSimulating}
            className="w-full py-4 bg-f1-red hover:bg-f1-red-hover text-white rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-f1-red/20 disabled:opacity-50"
          >
            {isSimulating ? <RefreshCw className="animate-spin" /> : <Play fill="currentColor" size={20} />}
            {isSimulating ? "Running Monte Carlo..." : "Run Simulation"}
          </button>
        </div>

        {/* Right Column: Visualizations & Output */}
        <div className="flex flex-col gap-6 xl:col-span-2">
          
          {/* Results Cards */}
          <AnimatePresence mode="popLayout">
            {simResults && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
              >
                <div className="glass-panel p-6 rounded-2xl border-l-4 border-f1-red">
                  <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Predicted Position</p>
                  <p className="text-4xl font-bold font-mono">P{simResults.pos}</p>
                </div>
                <div className="glass-panel p-6 rounded-2xl border-l-4 border-blue-500">
                  <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Race Time</p>
                  <p className="text-3xl font-bold font-mono">{simResults.time}</p>
                </div>
                <div className="glass-panel p-6 rounded-2xl border-l-4 border-yellow-500">
                  <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Strategy Risk</p>
                  <p className={`text-2xl font-bold ${simResults.risk.includes('HIGH') ? 'text-f1-red' : 'text-green-500'}`}>{simResults.risk}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Tire Wear Chart */}
          <div className="glass-panel p-6 rounded-2xl flex-1 min-h-[400px] flex flex-col">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Car className="text-gray-300" size={20} /> Tire Degradation Curve
            </h3>
            
            <div className="flex-1 w-full relative">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={wearData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="lap" stroke="#555" />
                  <YAxis stroke="#555" domain={[0, 100]} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    labelFormatter={(v) => `Lap ${v}`}
                  />
                  
                  {/* Highlight SC Events */}
                  {events.filter(e => e.active && e.type === "SC").map(sc => (
                    <ReferenceArea key={sc.id} x1={sc.start} x2={sc.end} fill="rgba(234, 179, 8, 0.1)" strokeOpacity={0} />
                  ))}
                  
                  {/* Highlight Rain Events */}
                  {events.filter(e => e.active && e.type === "Rain").map(rain => (
                    <ReferenceArea key={rain.id} x1={rain.start} x2={rain.end} fill="rgba(59, 130, 246, 0.1)" strokeOpacity={0} />
                  ))}

                  {/* Draw different line segments based on compound using stroke URL or just splitting data. For simplicity here, one line. */}
                  <Line 
                    type="monotone" 
                    dataKey="wear" 
                    stroke="var(--f1-red)" 
                    strokeWidth={3} 
                    dot={false}
                    activeDot={{ r: 6, fill: "var(--f1-red)" }}
                  />
                </LineChart>
              </ResponsiveContainer>
              
              {/* Reference Legend */}
              <div className="absolute top-0 right-4 flex gap-4 text-xs font-medium">
                {events.find(e => e.type === "SC")?.active && (
                  <div className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-500/20 border border-yellow-500 rounded-sm"></div> SC Period</div>
                )}
                {events.find(e => e.type === "Rain")?.active && (
                  <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500/20 border border-blue-500 rounded-sm"></div> Rain Period</div>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
