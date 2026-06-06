
import { useHealthCheck, useActiveModels } from '../../hooks/useApi';
import { Activity, Server, Database, AlertCircle } from 'lucide-react';
import { Skeleton } from '../../components/ui/Skeleton';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useHealthCheck();
  const { data: models, isLoading: modelsLoading } = useActiveModels();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Platform Overview</h1>
        <p className="text-gray-400 mt-1">Real-time status of the F1 AI Prediction Engine</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* System Status Card */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity">
            <Server className="w-16 h-16 text-f1-red" />
          </div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">API Status</h3>
          {healthLoading ? <Skeleton className="h-10 w-24" /> : (
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-f1-red'}`} />
              <span className="text-2xl font-bold">{health?.status === 'healthy' ? 'Online' : 'Offline'}</span>
            </div>
          )}
        </div>

        {/* Models Loaded Card */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity">
            <Database className="w-16 h-16 text-f1-neon" />
          </div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Active Models</h3>
          {modelsLoading ? <Skeleton className="h-10 w-24" /> : (
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold font-mono">
                {models?.active_models ? Object.keys(models.active_models).filter(k => models.active_models[k]).length : 0}
              </span>
              <span className="text-sm text-gray-500">Loaded in Memory</span>
            </div>
          )}
        </div>

        {/* Prediction Engine Card */}
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity">
            <Activity className="w-16 h-16 text-emerald-500" />
          </div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Inference Engine</h3>
          {healthLoading ? <Skeleton className="h-10 w-24" /> : (
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold">{health?.model_loaded ? 'Ready' : 'Standby'}</span>
            </div>
          )}
        </div>
      </div>

      <div className="glass-panel rounded-xl p-6 min-h-[300px]">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-f1-red" />
          Recent Activity
        </h2>
        <div className="flex flex-col items-center justify-center h-[200px] text-gray-500">
          <AlertCircle className="w-10 h-10 mb-2 opacity-50" />
          <p>No recent prediction logs found.</p>
        </div>
      </div>
    </div>
  );
}
