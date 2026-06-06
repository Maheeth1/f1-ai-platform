import { Zap, Network } from 'lucide-react';
import { useModelInfo } from '../../hooks/useApi';
import { Skeleton } from '../../components/ui/Skeleton';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const mockShapData = [
  { feature: 'Grid Position', importance: 0.85 },
  { feature: 'Tyre Age', importance: 0.65 },
  { feature: 'Driver Elo', importance: 0.55 },
  { feature: 'Track Temp', importance: 0.35 },
  { feature: 'Car Performance', importance: 0.45 },
].sort((a, b) => b.importance - a.importance);

export default function ModelInsights() {
  const { data: modelInfo, isLoading } = useModelInfo();

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Insights Layer</h1>
        <p className="text-gray-400 mt-1">Deep dive into model interpretability and validation metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Architecture */}
        <div className="glass-panel rounded-xl p-6 lg:col-span-1 border-t-2 border-t-cyan-500">
          <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
            <Network className="w-5 h-5 text-cyan-400" />
            Active Architecture
          </h2>
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-8 w-5/6" />
            </div>
          ) : (
            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between py-2 border-b border-f1-border">
                <span className="text-gray-500">Algorithm</span>
                <span className="text-white font-bold">{modelInfo?.model_type || 'CatBoostRegressor'}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-f1-border">
                <span className="text-gray-500">Version</span>
                <span className="text-white">v2.1.0-prod</span>
              </div>
              <div className="flex justify-between py-2 border-b border-f1-border">
                <span className="text-gray-500">Training MAE</span>
                <span className="text-emerald-400">1.24 positions</span>
              </div>
              <div className="pt-4">
                <span className="text-xs text-gray-500 uppercase block mb-2">Enabled Features</span>
                <div className="flex gap-2 flex-wrap">
                  {(modelInfo?.features || ['Driver', 'LapNumber', 'TyreLife']).map((f: string) => (
                    <span key={f} className="bg-f1-dark border border-f1-border px-2 py-1 rounded text-xs text-gray-300 shadow-sm">{f}</span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Feature Importance (SHAP) */}
        <div className="glass-panel rounded-xl p-6 lg:col-span-2 border-t-2 border-t-f1-red flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Zap className="w-5 h-5 text-f1-red" />
              Global Feature Importance (SHAP Values)
            </h2>
            <span className="px-2 py-1 bg-f1-border rounded text-xs font-mono text-gray-400">Mock Display Data</span>
          </div>
          
          <div className="flex-1 w-full min-h-[250px] -ml-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockShapData} layout="vertical" margin={{ top: 0, right: 0, left: 40, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="feature" type="category" stroke="#888d96" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: '#23252f', opacity: 0.4 }}
                  contentStyle={{ backgroundColor: '#151620', borderColor: '#23252f', borderRadius: '8px' }}
                />
                <Bar dataKey="importance" fill="#e10600" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-500 mt-4 italic">SHAP (SHapley Additive exPlanations) values indicate how much each feature contributes to pushing the model output from the base value to the final prediction.</p>
        </div>
      </div>
    </div>
  );
}
