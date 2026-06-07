"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Gauge, Zap, Flame, ThermometerSun } from "lucide-react";

// Mock data: A simple loop resembling a generic F1 circuit (like Monza)
// We break the track into segments for heatmap coloring
const FALLBACK_TRACK_SEGMENTS = Array.from({ length: 100 }).map((_, i) => {
  const t = i / 100;
  const angle = t * Math.PI * 2;
  
  // Create a shape: start with a circle, distort it to look like a track
  const rx = 300;
  const ry = 150;
  let x = Math.cos(angle) * rx;
  let y = Math.sin(angle) * ry;
  
  // Add some chicanes and straights
  if (t > 0.1 && t < 0.2) y += Math.sin((t - 0.1) * Math.PI * 10) * 20; // chicane
  if (t > 0.6 && t < 0.7) x -= Math.sin((t - 0.6) * Math.PI * 10) * 30; // chicane

  // Simulate Telemetry data at this point
  const speed = 100 + Math.abs(Math.sin(angle * 2)) * 220; // 100 to 320 km/h
  const throttle = speed > 250 ? 100 : Math.max(0, (speed - 100) / 1.5);
  const brake = speed < 150 && throttle === 0 ? 100 : 0;
  const gear = Math.max(2, Math.min(8, Math.floor(speed / 40)));
  const rpm = 10000 + (speed % 40) * 50;

  return { 
    id: i, 
    x: x + 400, // offset to center in 800x400 viewBox
    y: y + 200, 
    telemetry: { speed, throttle, brake, gear, rpm } 
  };
});

type HeatmapMode = "speed" | "throttle" | "brake" | "none";

export default function TrackIntelligence() {
  const [trackSegments, setTrackSegments] = useState(FALLBACK_TRACK_SEGMENTS);
  const [hoveredPoint, setHoveredPoint] = useState<typeof FALLBACK_TRACK_SEGMENTS[0] | null>(null);
  const [mode, setMode] = useState<HeatmapMode>("none");

  useEffect(() => {
    fetch("http://localhost:8001/api/data/track/2023/Monaco")
      .then(res => res.json())
      .then(data => {
        if(data.segments && data.segments.length > 0) {
          const mapped = data.segments.map((seg: any, i: number) => ({
            ...seg,
            id: i
          }));
          setTrackSegments(mapped);
        }
      })
      .catch(console.error);
  }, []);

  // Determine color based on mode
  const getColor = (segment: typeof FALLBACK_TRACK_SEGMENTS[0]) => {
    if (mode === "none") return "#ffffff";
    if (mode === "speed") {
      const s = segment.telemetry.speed;
      if (s > 280) return "#22c55e"; // Green = Fast
      if (s > 200) return "#eab308"; // Yellow = Medium
      return "#ef4444"; // Red = Slow
    }
    if (mode === "throttle") {
      return `rgba(34, 197, 94, ${segment.telemetry.throttle / 100})`;
    }
    if (mode === "brake") {
      return `rgba(239, 68, 68, ${segment.telemetry.brake / 100})`;
    }
    return "#ffffff";
  };

  return (
    <div className="flex flex-col flex-1 p-6 md:p-10 max-w-[1600px] mx-auto w-full">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">Interactive Track Intelligence</h1>
          <p className="text-gray-400">Hover over the track to view corner-by-corner telemetry analysis.</p>
        </div>
        
        <div className="flex bg-white/5 p-1 rounded-lg border border-white/10">
          <ModeButton active={mode === "none"} onClick={() => setMode("none")}>Standard</ModeButton>
          <ModeButton active={mode === "speed"} onClick={() => setMode("speed")}>Speed Map</ModeButton>
          <ModeButton active={mode === "throttle"} onClick={() => setMode("throttle")}>Throttle Map</ModeButton>
          <ModeButton active={mode === "brake"} onClick={() => setMode("brake")}>Brake Map</ModeButton>
        </div>
      </div>

      <div className="flex flex-col xl:flex-row gap-8 items-start">
        {/* Track Area */}
        <div className="glass-panel p-8 rounded-3xl flex-1 w-full relative overflow-hidden min-h-[500px] flex items-center justify-center">
          {/* SVG Track */}
          <svg viewBox="0 0 800 400" className="w-full h-full drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
            {/* Draw Path Segments for Heatmap */}
            {trackSegments.map((seg, i) => {
              const next = trackSegments[(i + 1) % trackSegments.length];
              return (
                <line
                  key={`line-${seg.id}`}
                  x1={seg.x}
                  y1={seg.y}
                  x2={next.x}
                  y2={next.y}
                  stroke={getColor(seg)}
                  strokeWidth={mode === "none" ? 6 : 10}
                  strokeLinecap="round"
                  className="transition-colors duration-500"
                />
              );
            })}

            {/* Interactive Overlay Points */}
            {trackSegments.map((seg) => (
              <circle
                key={`point-${seg.id}`}
                cx={seg.x}
                cy={seg.y}
                r={12}
                fill="transparent"
                className="cursor-crosshair"
                onMouseEnter={() => setHoveredPoint(seg)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
            ))}

            {/* Hover Indicator */}
            {hoveredPoint && (
              <circle
                cx={hoveredPoint.x}
                cy={hoveredPoint.y}
                r={6}
                fill="#e10600"
                className="animate-ping"
              />
            )}
          </svg>
        </div>

        {/* Telemetry Panel */}
        <div className="w-full xl:w-[400px] flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Zap className="text-f1-red" /> Live Telemetry
            </h3>
            
            {hoveredPoint ? (
              <AnimatePresence mode="wait">
                <motion.div
                  key={hoveredPoint.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-6"
                >
                  {/* Speed & Gear */}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm mb-1 uppercase tracking-wider">Speed</p>
                      <p className="text-4xl font-bold font-mono">{Math.round(hoveredPoint.telemetry.speed)} <span className="text-lg text-gray-500">km/h</span></p>
                    </div>
                    <div className="text-right">
                      <p className="text-gray-400 text-sm mb-1 uppercase tracking-wider">Gear</p>
                      <p className="text-4xl font-bold font-mono text-f1-red">{hoveredPoint.telemetry.gear}</p>
                    </div>
                  </div>

                  {/* RPM */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400 uppercase tracking-wider">RPM</span>
                      <span className="font-mono">{Math.round(hoveredPoint.telemetry.rpm)}</span>
                    </div>
                    <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500" 
                        style={{ width: `${(hoveredPoint.telemetry.rpm / 14000) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Throttle & Brake */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider flex items-center gap-1"><Flame size={14} /> Throttle</p>
                      <p className="text-2xl font-bold font-mono text-green-500">{Math.round(hoveredPoint.telemetry.throttle)}%</p>
                    </div>
                    <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider flex items-center gap-1"><Gauge size={14} /> Brake</p>
                      <p className="text-2xl font-bold font-mono text-red-500">{Math.round(hoveredPoint.telemetry.brake)}%</p>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            ) : (
              <div className="h-[250px] flex items-center justify-center border-2 border-dashed border-white/10 rounded-xl">
                <p className="text-gray-500 text-sm text-center px-6">
                  Hover over the track map to view instant corner telemetry.
                </p>
              </div>
            )}
          </div>

          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <ThermometerSun className="text-yellow-500" /> Sector Analysis
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              The heatmap layers reveal critical performance insights. Switch to "Speed Map" to identify slow-speed corners vs high-speed straights, or use the "Throttle Map" to analyze driver confidence on corner exits.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModeButton({ active, onClick, children }: { active: boolean, onClick: () => void, children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
        active 
          ? "bg-white text-black shadow-lg" 
          : "text-gray-400 hover:text-white hover:bg-white/10"
      }`}
    >
      {children}
    </button>
  );
}
