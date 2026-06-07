"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import { Play, Pause, SkipBack, SkipForward, FastForward, Activity, AlertTriangle } from "lucide-react";

// Mock trace data representing a single lap comparison
const TRACE_DATA = Array.from({ length: 100 }).map((_, i) => {
  const distance = i * 50; // meters
  
  // Base speed curve
  const baseSpeed = 150 + Math.sin(i / 10) * 100;
  
  // VER is faster in fast corners and straights
  const verSpeed = baseSpeed + (baseSpeed > 200 ? 5 : -2) + Math.random() * 2;
  // NOR is faster under braking
  const norSpeed = baseSpeed + (baseSpeed < 180 ? 4 : -3) + Math.random() * 2;
  
  const verThrottle = verSpeed > 200 ? 100 : Math.max(0, (verSpeed - 100));
  const norThrottle = norSpeed > 200 ? 100 : Math.max(0, (norSpeed - 100));

  // Cumulative time delta calculation (mocked)
  const delta = Math.sin(i / 20) * 0.4 + (i / 100) * 0.2;

  return {
    distance,
    verSpeed: Math.round(verSpeed),
    norSpeed: Math.round(norSpeed),
    verThrottle: Math.round(verThrottle),
    norThrottle: Math.round(norThrottle),
    delta: Number(delta.toFixed(3))
  };
});

export default function Comparison() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0); // 0 to 100 representing percentage of lap
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // Playback loop
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setPlaybackTime((prev) => {
          if (prev >= 100) {
            setIsPlaying(false);
            return 100;
          }
          return prev + (0.5 * playbackSpeed);
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed]);

  const currentDataPoint = TRACE_DATA[Math.min(99, Math.floor(playbackTime))];
  const deltaColor = currentDataPoint.delta < 0 ? "#22c55e" : "#ef4444"; // Green if VER faster, Red if NOR faster
  const deltaPrefix = currentDataPoint.delta > 0 ? "+" : "";

  return (
    <div className="flex flex-col flex-1 p-6 md:p-10 max-w-[1600px] mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Driver Comparison & Replay</h1>
        <p className="text-gray-400">Side-by-side telemetry trace analysis and historical lap replay.</p>
      </div>

      {/* Driver Selectors & Live Delta */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-center items-center relative overflow-hidden border-t-4 border-[#0019bf]">
          <span className="absolute top-2 right-3 text-xs text-gray-500 font-bold tracking-widest uppercase">Driver A</span>
          <h2 className="text-4xl font-bold font-mono tracking-tighter mt-2">VER</h2>
          <p className="text-gray-400 text-sm">Red Bull Racing</p>
          <div className="mt-4 flex gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500 uppercase">Speed</p>
              <p className="text-xl font-bold text-[#0019bf]">{currentDataPoint.verSpeed} <span className="text-xs text-gray-500">km/h</span></p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">Throttle</p>
              <p className="text-xl font-bold text-[#0019bf]">{currentDataPoint.verThrottle}%</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-center items-center">
          <p className="text-sm text-gray-400 uppercase tracking-widest mb-2">Live Delta</p>
          <motion.div 
            key={currentDataPoint.delta}
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="text-5xl font-mono font-bold"
            style={{ color: deltaColor }}
          >
            {deltaPrefix}{currentDataPoint.delta.toFixed(3)}s
          </motion.div>
          <p className="text-xs text-gray-500 mt-2">
            {currentDataPoint.delta < 0 ? "VER is faster" : "NOR is faster"}
          </p>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-center items-center relative overflow-hidden border-t-4 border-[#ff8000]">
          <span className="absolute top-2 right-3 text-xs text-gray-500 font-bold tracking-widest uppercase">Driver B</span>
          <h2 className="text-4xl font-bold font-mono tracking-tighter mt-2">NOR</h2>
          <p className="text-gray-400 text-sm">McLaren</p>
          <div className="mt-4 flex gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500 uppercase">Speed</p>
              <p className="text-xl font-bold text-[#ff8000]">{currentDataPoint.norSpeed} <span className="text-xs text-gray-500">km/h</span></p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">Throttle</p>
              <p className="text-xl font-bold text-[#ff8000]">{currentDataPoint.norThrottle}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Replay Controls */}
      <div className="glass-panel p-6 rounded-2xl mb-8 flex flex-col md:flex-row items-center gap-6">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setPlaybackTime(0)}
            className="p-3 rounded-full hover:bg-white/10 transition-colors"
          >
            <SkipBack size={20} />
          </button>
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-4 rounded-full bg-f1-red hover:bg-f1-red-hover text-white transition-colors shadow-lg shadow-f1-red/20"
          >
            {isPlaying ? <Pause size={24} fill="currentColor" /> : <Play size={24} fill="currentColor" className="ml-1" />}
          </button>
          <button 
            onClick={() => setPlaybackTime(100)}
            className="p-3 rounded-full hover:bg-white/10 transition-colors"
          >
            <SkipForward size={20} />
          </button>
          <button 
            onClick={() => setPlaybackSpeed(s => s === 1 ? 2 : s === 2 ? 4 : 1)}
            className="p-3 rounded-full hover:bg-white/10 transition-colors flex items-center gap-1 text-sm font-bold"
          >
            <FastForward size={16} /> {playbackSpeed}x
          </button>
        </div>

        <div className="flex-1 w-full flex items-center gap-4">
          <span className="text-xs font-mono text-gray-400 w-12">LAP START</span>
          <input 
            type="range" 
            min="0" 
            max="100" 
            step="0.1"
            value={playbackTime} 
            onChange={(e) => setPlaybackTime(parseFloat(e.target.value))}
            className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-f1-red"
          />
          <span className="text-xs font-mono text-gray-400 w-12 text-right">LAP END</span>
        </div>
      </div>

      {/* Telemetry Traces */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Speed Trace */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <Activity className="text-f1-red" size={20} /> Speed Trace (km/h)
          </h3>
          <div className="h-[300px] w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={TRACE_DATA} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="distance" stroke="#555" tick={false} />
                <YAxis stroke="#555" tick={{ fill: '#888', fontSize: 12 }} domain={['dataMin - 20', 'dataMax + 20']} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  labelStyle={{ color: '#888', marginBottom: '8px' }}
                  labelFormatter={(v) => `Distance: ${v}m`}
                />
                
                {/* Playback Cursor Line */}
                <ReferenceLine x={currentDataPoint.distance} stroke="rgba(255,255,255,0.3)" strokeWidth={2} />

                <Line type="monotone" dataKey="verSpeed" name="VER" stroke="#0019bf" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                <Line type="monotone" dataKey="norSpeed" name="NOR" stroke="#ff8000" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Time Delta Trace */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <AlertTriangle className="text-yellow-500" size={20} /> Time Delta (s)
          </h3>
          <div className="h-[300px] w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={TRACE_DATA} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="distance" stroke="#555" tick={false} />
                <YAxis stroke="#555" tick={{ fill: '#888', fontSize: 12 }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(20,20,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  labelStyle={{ color: '#888', marginBottom: '8px' }}
                  labelFormatter={(v) => `Distance: ${v}m`}
                />
                <ReferenceLine y={0} stroke="#888" strokeDasharray="3 3" />
                
                {/* Playback Cursor Line */}
                <ReferenceLine x={currentDataPoint.distance} stroke="rgba(255,255,255,0.3)" strokeWidth={2} />

                <Line type="monotone" dataKey="delta" name="Delta (VER - NOR)" stroke="#e10600" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div className="absolute top-4 right-4 text-xs text-gray-500 flex flex-col gap-1 items-end">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Up = NOR Faster</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Down = VER Faster</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
