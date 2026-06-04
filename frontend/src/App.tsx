import React, { useState, useEffect } from 'react';
import { FormSlider } from './components/FormSlider';
import { 
  Zap, 
  Activity, 
  Settings, 
  TrendingUp, 
  AlertCircle, 
  RefreshCw,
  Award,
  Users
} from 'lucide-react';

// Driver mapping based on standard category codes
const DRIVERS = [
  { code: 0, name: 'Lando Norris', team: 'McLaren', number: 4 },
  { code: 1, name: 'Charles Leclerc', team: 'Ferrari', number: 16 },
  { code: 2, name: 'Oscar Piastri', team: 'McLaren', number: 81 },
  { code: 3, name: 'Max Verstappen', team: 'Red Bull Racing', number: 1 },
  { code: 4, name: 'Lewis Hamilton', team: 'Mercedes', number: 44 },
  { code: 5, name: 'Carlos Sainz', team: 'Ferrari', number: 55 },
  { code: 6, name: 'George Russell', team: 'Mercedes', number: 63 },
  { code: 7, name: 'Sergio Perez', team: 'Red Bull Racing', number: 11 },
  { code: 8, name: 'Fernando Alonso', team: 'Aston Martin', number: 14 },
  { code: 9, name: 'Pierre Gasly', team: 'Alpine', number: 10 },
  { code: 10, name: 'Esteban Ocon', team: 'Haas', number: 31 },
  { code: 11, name: 'Alex Albon', team: 'Williams', number: 23 },
  { code: 12, name: 'Yuki Tsunoda', team: 'RB', number: 22 },
  { code: 13, name: 'Nico Hulkenberg', team: 'Haas', number: 27 },
  { code: 14, name: 'Valtteri Bottas', team: 'Kick Sauber', number: 77 },
  { code: 15, name: 'Lance Stroll', team: 'Aston Martin', number: 18 },
  { code: 16, name: 'Kevin Magnussen', team: 'Haas', number: 20 },
  { code: 17, name: 'Logan Sargeant', team: 'Williams', number: 2 },
  { code: 18, name: 'Daniel Ricciardo', team: 'RB', number: 3 },
  { code: 19, name: 'Zhou Guanyu', team: 'Kick Sauber', number: 24 }
];

export default function App() {
  // Form State
  const [driver, setDriver] = useState<number>(3);
  const [lapNumber, setLapNumber] = useState<number>(20);
  const [tyreLife, setTyreLife] = useState<number>(10);

  // API State
  const [prediction, setPrediction] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // System Health
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'offline' | 'unloaded'>('offline');
  const [modelType, setModelType] = useState<string>('Unknown');
  const [modelFeatures, setModelFeatures] = useState<string[]>([]);
  const [checkingHealth, setCheckingHealth] = useState<boolean>(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

  // Check backend health
  const checkHealth = async () => {
    setCheckingHealth(true);
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'healthy') {
          setHealthStatus(data.model_loaded ? 'healthy' : 'unloaded');
          // Fetch model info if healthy
          if (data.model_loaded) {
            const infoRes = await fetch(`${API_BASE_URL}/model-info`);
            if (infoRes.ok) {
              const infoData = await infoRes.json();
              setModelType(infoData.model_type || 'Unknown');
              setModelFeatures(infoData.features || []);
            }
          }
        } else {
          setHealthStatus('unloaded');
        }
      } else {
        setHealthStatus('offline');
      }
    } catch (e) {
      setHealthStatus('offline');
    } finally {
      setCheckingHealth(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  // Fetch a sample request from backend
  const loadBackendSample = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/sample-request`);
      if (res.ok) {
        const data = await res.json();
        setDriver(data.Driver ?? 5);
        setLapNumber(data.LapNumber ?? 20);
        setTyreLife(data.TyreLife ?? 15);
      }
    } catch (e) {
      console.error('Failed to load sample from API:', e);
    }
  };

  // Preset Handlers
  const loadPreset = (d: number, l: number, t: number) => {
    setDriver(d);
    setLapNumber(l);
    setTyreLife(t);
  };

  // Submit prediction request
  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Driver: driver,
          LapNumber: lapNumber,
          TyreLife: tyreLife,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setPrediction(data.predicted_position);
      } else {
        const errorData = await res.json().catch(() => ({}));
        setError(errorData.detail || 'Prediction failed. Please check your backend connection.');
      }
    } catch (e) {
      setError('Cannot connect to the prediction server. Make sure your FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to format predicted position styles
  const getPositionStyling = (pos: number) => {
    if (pos <= 3.5) {
      return {
        bg: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
        glow: 'shadow-[0_0_30px_rgba(234,179,8,0.25)]',
        badge: '🏆 Podium Contender',
      };
    } else if (pos <= 10.5) {
      return {
        bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
        glow: 'shadow-[0_0_30px_rgba(6,182,212,0.25)]',
        badge: '🏁 Points Finish',
      };
    } else {
      return {
        bg: 'bg-gray-700/10 border-gray-700/30 text-gray-400',
        glow: 'shadow-[0_0_20px_rgba(156,163,175,0.05)]',
        badge: '⏱️ Midfield/Back Grid',
      };
    }
  };

  return (
    <div className="min-h-screen bg-f1-dark text-white carbon-grid pb-12">
      {/* Navbar */}
      <nav className="border-b border-f1-border bg-f1-dark/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded bg-f1-red flex items-center justify-center font-black text-xl tracking-tighter text-white select-none">
              F1
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wider m-0 leading-tight">AI PLATFORM</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Race Prediction Engine</p>
            </div>
          </div>

          {/* Connection Status Badge */}
          <div className="flex items-center gap-4">
            <button 
              onClick={checkHealth}
              disabled={checkingHealth}
              className="p-1.5 rounded-lg border border-f1-border hover:bg-f1-border/40 text-gray-400 transition"
              title="Refresh connection status"
            >
              <RefreshCw className={`w-4 h-4 ${checkingHealth ? 'animate-spin text-f1-neon' : ''}`} />
            </button>
            
            {healthStatus === 'healthy' && (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                API Connected
              </span>
            )}
            {healthStatus === 'unloaded' && (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                Model Missing
              </span>
            )}
            {healthStatus === 'offline' && (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-f1-red/10 text-f1-neon border border-f1-red/20 shadow-[0_0_10px_rgba(225,6,0,0.15)]">
                <span className="w-2 h-2 rounded-full bg-f1-red"></span>
                API Offline
              </span>
            )}
          </div>
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-4 mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Hand: Controls and Presets */}
        <section className="lg:col-span-7 space-y-6">
          
          {/* Preset Panel */}
          <div className="glass-panel rounded-xl p-5 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-f1-red/5 rounded-bl-full pointer-events-none"></div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-f1-gray mb-4 font-mono flex items-center gap-2">
              <Zap className="w-4 h-4 text-f1-red" />
              Quick Race Presets
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                onClick={() => loadPreset(3, 5, 2)}
                className="flex flex-col items-start p-3 rounded-lg border border-f1-border bg-f1-dark/40 hover:bg-f1-red/5 hover:border-f1-red/30 transition text-left group"
              >
                <span className="text-xs font-bold text-gray-300 group-hover:text-white transition">Podium Pace</span>
                <span className="text-[10px] text-gray-500 font-mono mt-1">Verstappen (#1) • Lap 5 • Tyre 2</span>
              </button>
              <button
                onClick={() => loadPreset(4, 30, 18)}
                className="flex flex-col items-start p-3 rounded-lg border border-f1-border bg-f1-dark/40 hover:bg-f1-red/5 hover:border-f1-red/30 transition text-left group"
              >
                <span className="text-xs font-bold text-gray-300 group-hover:text-white transition">Mid-Race Battle</span>
                <span className="text-[10px] text-gray-500 font-mono mt-1">Hamilton (#4) • Lap 30 • Tyre 18</span>
              </button>
              <button
                onClick={() => loadPreset(1, 65, 5)}
                className="flex flex-col items-start p-3 rounded-lg border border-f1-border bg-f1-dark/40 hover:bg-f1-red/5 hover:border-f1-red/30 transition text-left group"
              >
                <span className="text-xs font-bold text-gray-300 group-hover:text-white transition">Late Charge</span>
                <span className="text-[10px] text-gray-500 font-mono mt-1">Leclerc (#16) • Lap 65 • Tyre 5</span>
              </button>
            </div>
            
            <div className="mt-4 pt-3 border-t border-f1-border flex justify-between items-center">
              <span className="text-xs text-gray-500">Or use the sample request parameters from backend:</span>
              <button 
                onClick={loadBackendSample}
                className="text-xs font-mono font-bold text-f1-neon hover:underline bg-transparent border-0 cursor-pointer p-0"
              >
                Fetch API Sample
              </button>
            </div>
          </div>

          {/* Form Panel */}
          <div className="glass-panel rounded-xl p-6 shadow-2xl relative">
            <h2 className="text-lg font-bold mb-6 tracking-wide flex items-center gap-2">
              <Settings className="w-5 h-5 text-f1-red" />
              Configure Race Parameters
            </h2>
            
            <form onSubmit={handlePredict} className="space-y-6">
              
              {/* Driver Dropdown Selector */}
              <div className="flex flex-col space-y-2">
                <label className="flex items-center text-sm font-medium text-gray-400 gap-2">
                  <Users className="w-4 h-4 text-f1-red" />
                  Select F1 Driver
                </label>
                <div className="relative">
                  <select
                    value={driver}
                    onChange={(e) => setDriver(Number(e.target.value))}
                    className="w-full bg-f1-dark border border-f1-border rounded-lg px-4 py-3 text-white appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-f1-neon focus:border-f1-red/50 transition-all font-medium"
                  >
                    {DRIVERS.map((d) => (
                      <option key={d.code} value={d.code} className="bg-f1-card text-white">
                        {d.name} (#{d.number}) — {d.team}
                      </option>
                    ))}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                      <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Lap Number Slider */}
              <FormSlider
                label="Current Lap Number"
                value={lapNumber}
                min={1}
                max={78}
                onChange={setLapNumber}
                icon={<Activity className="w-4 h-4" />}
                unit=""
              />

              {/* Tyre Life Slider */}
              <FormSlider
                label="Tyre Age (Laps run on current set)"
                value={tyreLife}
                min={0}
                max={50}
                onChange={setTyreLife}
                icon={<TrendingUp className="w-4 h-4" />}
                unit=" Laps"
              />

              {/* Predict Trigger Button */}
              <button
                type="submit"
                disabled={loading || healthStatus === 'offline'}
                className={`w-full py-4 rounded-lg font-bold tracking-wider uppercase transition-all duration-300 transform select-none relative overflow-hidden flex items-center justify-center gap-3
                  ${healthStatus === 'offline' 
                    ? 'bg-gray-800 text-gray-500 border border-gray-700 cursor-not-allowed'
                    : 'bg-f1-red hover:bg-f1-neon hover:scale-[1.01] active:scale-100 text-white shadow-[0_0_20px_rgba(225,6,0,0.3)] hover:shadow-[0_0_25px_rgba(225,6,0,0.5)] cursor-pointer'
                  }`}
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Executing Prediction Run...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Execute Race Prediction
                  </>
                )}
              </button>
            </form>
          </div>
        </section>

        {/* Right Hand: Prediction Output & Model info */}
        <section className="lg:col-span-5 space-y-6">
          
          {/* Prediction Result Display */}
          <div className={`glass-panel rounded-xl p-6 shadow-2xl relative flex flex-col items-center justify-center min-h-[350px] transition-all duration-500 overflow-hidden 
            ${prediction !== null ? getPositionStyling(prediction).bg : ''}`}>
            
            {prediction !== null && (
              <div className={`absolute inset-0 bg-radial-gradient opacity-10 pointer-events-none`}></div>
            )}

            {loading ? (
              // Loading/Scanning effect
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full border-4 border-f1-border border-t-f1-red animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Activity className="w-6 h-6 text-f1-neon animate-pulse" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-sm font-mono text-f1-neon uppercase tracking-widest animate-pulse">Running telemetry analysis</p>
                  <p className="text-xs text-gray-500 mt-1">Simulating race finishes based on track wear...</p>
                </div>
              </div>
            ) : prediction !== null ? (
              // Realized prediction details
              <div className="w-full flex flex-col items-center text-center space-y-6 animate-fadeIn">
                <div className={`px-4 py-1.5 rounded-full text-xs font-mono font-bold tracking-wide border ${getPositionStyling(prediction).bg}`}>
                  {getPositionStyling(prediction).badge}
                </div>

                <div className="relative">
                  {/* Glowing background container */}
                  <div className={`absolute inset-0 rounded-full blur-3xl opacity-30 ${getPositionStyling(prediction).glow}`}></div>
                  
                  {/* Big Position Display */}
                  <div className="relative w-40 h-40 rounded-full border-4 border-f1-red/30 flex flex-col items-center justify-center bg-f1-dark/80 pulse-neon-border">
                    <span className="text-xs font-mono text-gray-400 uppercase tracking-widest">Predicted</span>
                    <span className="text-6xl font-black tracking-tight text-white font-mono mt-1">
                      P{Math.max(1, Math.round(prediction))}
                    </span>
                    <span className="text-[10px] text-gray-500 font-mono mt-1">Position finish</span>
                  </div>
                </div>

                {/* Predictor stats breakdown */}
                <div className="w-full bg-f1-dark/50 border border-f1-border rounded-lg p-4 grid grid-cols-2 gap-4 text-left">
                  <div>
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider font-mono">Driver Incar</p>
                    <p className="text-sm font-bold mt-0.5 text-white">{DRIVERS.find(d => d.code === driver)?.name}</p>
                    <p className="text-xs text-f1-gray font-mono">#{DRIVERS.find(d => d.code === driver)?.number}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider font-mono">Stint Context</p>
                    <p className="text-sm font-bold mt-0.5 text-white">Lap {lapNumber} / 78</p>
                    <p className="text-xs text-f1-gray font-mono">{tyreLife} lap tyre age</p>
                  </div>
                </div>

                <p className="text-xs text-gray-500 italic max-w-[280px]">
                  Prediction reflects simulated final position under dry weather race conditions at Monaco.
                </p>
              </div>
            ) : error ? (
              // Error state
              <div className="flex flex-col items-center justify-center text-center p-4 space-y-4">
                <AlertCircle className="w-12 h-12 text-f1-neon" />
                <div>
                  <h3 className="font-bold text-white text-base">Prediction Run Failed</h3>
                  <p className="text-xs text-gray-400 mt-2 max-w-xs">{error}</p>
                </div>
                <button
                  onClick={checkHealth}
                  className="px-4 py-2 rounded border border-f1-border hover:bg-f1-border/40 text-xs font-bold transition cursor-pointer"
                >
                  Diagnose connection
                </button>
              </div>
            ) : (
              // Empty state
              <div className="flex flex-col items-center justify-center text-center p-6 space-y-4">
                <Award className="w-16 h-16 text-gray-700 animate-pulse" />
                <div>
                  <h3 className="font-bold text-gray-400 text-lg uppercase tracking-wider">Awaiting Telemetry</h3>
                  <p className="text-xs text-gray-500 max-w-xs mt-2 leading-relaxed">
                    Configure the race parameters, choose a driver on grid, and click "Execute Race Prediction" to evaluate performance.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Model & Infrastructure Info */}
          <div className="glass-panel rounded-xl p-5 shadow-2xl space-y-4 text-xs">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-f1-gray font-mono flex items-center gap-2">
              <Settings className="w-4 h-4 text-f1-red" />
              Machine Learning Specs
            </h2>
            <div className="space-y-2.5 font-mono">
              <div className="flex justify-between py-1 border-b border-f1-border/50">
                <span className="text-gray-500">Repository Source:</span>
                <span className="text-gray-300 text-right truncate max-w-[220px]" title="Maheeth1/f1-race-predictor">
                  Hugging Face Hub
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-f1-border/50">
                <span className="text-gray-500">Model Pipeline:</span>
                <span className="text-gray-300">{modelType}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-f1-border/50">
                <span className="text-gray-500">Target Feature:</span>
                <span className="text-emerald-400 font-bold">Position</span>
              </div>
              <div className="flex justify-between py-1 border-b border-f1-border/50">
                <span className="text-gray-500">Model Features:</span>
                <div className="flex flex-wrap gap-1 justify-end max-w-[200px]">
                  {modelFeatures.length > 0 ? (
                    modelFeatures.map(f => (
                      <span key={f} className="px-1.5 py-0.5 bg-f1-border/60 rounded text-[9px] text-gray-300">
                        {f}
                      </span>
                    ))
                  ) : (
                    <span className="text-gray-500 italic">None loaded</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}
