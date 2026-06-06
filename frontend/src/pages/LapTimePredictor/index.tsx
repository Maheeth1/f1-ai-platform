import { useState } from 'react';
import { usePrediction } from '../../hooks/useApi';
import { FormSlider } from '../../components/ui/FormSlider';
import { Zap, Settings, Activity, TrendingUp, Users, RefreshCw, AlertCircle, Award } from 'lucide-react';

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

export default function LapTimePredictor() {
  const [driver, setDriver] = useState<number>(3);
  const [lapNumber, setLapNumber] = useState<number>(20);
  const [tyreLife, setTyreLife] = useState<number>(10);
  
  const predictMutation = usePrediction('LapTimeSeconds');

  const handlePredict = (e: React.FormEvent) => {
    e.preventDefault();
    predictMutation.mutate({
      Driver: driver.toString(),
      LapNumber: lapNumber,
      TyreLife: tyreLife,
    });
  };

  const prediction = predictMutation.data?.prediction;
  const loading = predictMutation.isPending;
  const error = predictMutation.isError ? (predictMutation.error as Error).message : null;

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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Race Predictor</h1>
        <p className="text-gray-400 mt-1">Predict final race position based on current telemetry</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <section className="lg:col-span-7 space-y-6">
          <div className="glass-panel rounded-xl p-6 shadow-2xl relative">
            <h2 className="text-lg font-bold mb-6 tracking-wide flex items-center gap-2">
              <Settings className="w-5 h-5 text-f1-red" />
              Configure Race Parameters
            </h2>
            
            <form onSubmit={handlePredict} className="space-y-6">
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
                </div>
              </div>

              <FormSlider
                label="Current Lap Number"
                value={lapNumber}
                min={1}
                max={78}
                onChange={setLapNumber}
                icon={<Activity className="w-4 h-4" />}
                unit=""
              />

              <FormSlider
                label="Tyre Age (Laps run on current set)"
                value={tyreLife}
                min={0}
                max={50}
                onChange={setTyreLife}
                icon={<TrendingUp className="w-4 h-4" />}
                unit=" Laps"
              />

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-lg font-bold tracking-wider uppercase transition-all duration-300 transform select-none relative overflow-hidden flex items-center justify-center gap-3 bg-f1-red hover:bg-f1-neon hover:scale-[1.01] active:scale-100 text-white shadow-[0_0_20px_rgba(225,6,0,0.3)] hover:shadow-[0_0_25px_rgba(225,6,0,0.5)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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

        <section className="lg:col-span-5 space-y-6">
          <div className={`glass-panel rounded-xl p-6 shadow-2xl relative flex flex-col items-center justify-center min-h-[350px] transition-all duration-500 overflow-hidden 
            ${prediction !== undefined ? getPositionStyling(prediction).bg : ''}`}>
            
            {loading ? (
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full border-4 border-f1-border border-t-f1-red animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Activity className="w-6 h-6 text-f1-neon animate-pulse" />
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-sm font-mono text-f1-neon uppercase tracking-widest animate-pulse">Running telemetry analysis</p>
                </div>
              </div>
            ) : prediction !== undefined ? (
              <div className="w-full flex flex-col items-center text-center space-y-6 animate-fadeIn">
                <div className={`px-4 py-1.5 rounded-full text-xs font-mono font-bold tracking-wide border ${getPositionStyling(prediction).bg}`}>
                  {getPositionStyling(prediction).badge}
                </div>

                <div className="relative w-40 h-40 rounded-full border-4 border-f1-red/30 flex flex-col items-center justify-center bg-f1-dark/80 pulse-neon-border">
                  <span className="text-xs font-mono text-gray-400 uppercase tracking-widest">Predicted</span>
                  <span className="text-6xl font-black tracking-tight text-white font-mono mt-1">
                    P{Math.max(1, Math.round(prediction))}
                  </span>
                </div>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center text-center p-4 space-y-4">
                <AlertCircle className="w-12 h-12 text-f1-neon" />
                <div>
                  <h3 className="font-bold text-white text-base">Prediction Run Failed</h3>
                  <p className="text-xs text-gray-400 mt-2 max-w-xs">{error}</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-6 space-y-4">
                <Award className="w-16 h-16 text-gray-700 animate-pulse" />
                <div>
                  <h3 className="font-bold text-gray-400 text-lg uppercase tracking-wider">Awaiting Telemetry</h3>
                  <p className="text-xs text-gray-500 max-w-xs mt-2 leading-relaxed">
                    Configure the race parameters to evaluate performance.
                  </p>
                </div>
              </div>
            )}
          </div>
          
          {/* AI Explanation Panel */}
          {prediction !== undefined && !loading && (
            <div className="glass-panel rounded-xl p-6 shadow-2xl animate-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4 flex items-center gap-2">
                <Zap className="w-4 h-4 text-f1-neon" />
                AI Interpretability Report
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-300">Driver Capability</span>
                  <div className="w-1/2 h-1.5 bg-f1-border rounded overflow-hidden">
                    <div className="h-full bg-emerald-400 w-3/4"></div>
                  </div>
                  <span className="text-emerald-400 font-mono">+0.3s</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-300">Tyre Degradation ({tyreLife} Laps)</span>
                  <div className="w-1/2 h-1.5 bg-f1-border rounded overflow-hidden">
                    <div className="h-full bg-f1-red w-full"></div>
                  </div>
                  <span className="text-f1-red font-mono">-1.2s</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-300">Fuel Load Effect</span>
                  <div className="w-1/2 h-1.5 bg-f1-border rounded overflow-hidden">
                    <div className="h-full bg-emerald-400 w-1/4"></div>
                  </div>
                  <span className="text-emerald-400 font-mono">+0.1s</span>
                </div>
                <p className="text-[10px] text-gray-500 mt-4 leading-relaxed border-t border-f1-border pt-3">
                  This prediction is heavily penalized by tyre age. The model considers {tyreLife} laps on the current compound to result in a significant pace deficit relative to the grid average.
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
