import { useEffect, useState } from 'react';
import { useHealthCheck, useActiveModels } from '../../hooks/useApi';
import { Activity, Server, Database, TrendingUp, Zap } from 'lucide-react';
import { Skeleton } from '../../components/ui/Skeleton';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useHealthCheck();
  const { data: models, isLoading: modelsLoading } = useActiveModels();

  // Mock real-time data for system health graph
  const [cpuData, setCpuData] = useState<{ time: number; usage: number }[]>(
    Array.from({ length: 20 }, (_, i) => ({ time: i, usage: 30 + Math.random() * 20 }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setCpuData(prev => {
        const newData = [...prev.slice(1), { time: prev[prev.length - 1].time + 1, usage: 30 + Math.random() * 20 }];
        return newData;
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Real-Time Analytics Dashboard</h1>
        <p className="text-gray-400 mt-1">Live metrics and model status for the F1 AI Prediction Engine</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* API Status */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden group hover:-translate-y-1 transition-transform">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Server className="w-12 h-12 text-f1-red" />
          </div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 font-mono">API Node Status</h3>
          {healthLoading ? <Skeleton className="h-8 w-24" /> : (
            <div className="flex items-center gap-2">
              <div className={`w-2.5 h-2.5 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse' : 'bg-f1-red'}`} />
              <span className="text-xl font-bold font-mono">{health?.status === 'healthy' ? 'CONNECTED' : 'OFFLINE'}</span>
            </div>
          )}
        </div>

        {/* Active Models */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden group hover:-translate-y-1 transition-transform border-t-2 border-t-cyan-500">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Database className="w-12 h-12 text-cyan-400" />
          </div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 font-mono">Loaded Models</h3>
          {modelsLoading ? <Skeleton className="h-8 w-16" /> : (
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono text-cyan-400 shadow-cyan-400 drop-shadow-sm">
                {models?.active_models ? Object.keys(models.active_models).filter(k => models.active_models[k]).length : 0}
              </span>
              <span className="text-xs text-gray-500">In Memory</span>
            </div>
          )}
        </div>

        {/* Prediction Count (Mock Animated) */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden group hover:-translate-y-1 transition-transform border-t-2 border-t-f1-neon">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Zap className="w-12 h-12 text-f1-neon" />
          </div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 font-mono">24h Inferences</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-white">14,208</span>
            <span className="text-xs text-emerald-400 flex items-center"><TrendingUp className="w-3 h-3 mr-0.5"/> 12%</span>
          </div>
        </div>

        {/* Latency */}
        <div className="glass-panel p-5 rounded-xl relative overflow-hidden group hover:-translate-y-1 transition-transform">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Activity className="w-12 h-12 text-emerald-500" />
          </div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3 font-mono">Avg Latency</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-white">42</span>
            <span className="text-xs text-gray-500">ms</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Load Chart */}
        <div className="glass-panel rounded-xl p-6 lg:col-span-2 min-h-[300px] flex flex-col">
          <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            Inference Engine CPU Load
          </h2>
          <div className="flex-1 w-full h-full relative -ml-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cpuData}>
                <YAxis domain={[0, 100]} hide />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="#10b981" 
                  strokeWidth={2} 
                  dot={false} 
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Active Model versions list */}
        <div className="glass-panel rounded-xl p-6 flex flex-col">
          <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4 flex items-center gap-2">
            <Server className="w-4 h-4 text-f1-red" />
            Registry
          </h2>
          {modelsLoading ? (
             <div className="space-y-4"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
            <div className="space-y-3 flex-1 overflow-y-auto pr-2">
              {models?.active_models && Object.entries(models.active_models).map(([target, info]: [string, any]) => (
                <div key={target} className="bg-f1-dark/60 border border-f1-border p-3 rounded-lg flex flex-col gap-1">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white uppercase">{target}</span>
                    <span className={`w-2 h-2 rounded-full ${info ? 'bg-emerald-500' : 'bg-gray-600'}`} />
                  </div>
                  <span className="text-[10px] text-gray-400 font-mono truncate">{info ? info.version : 'Not Loaded'}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
