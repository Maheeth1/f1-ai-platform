
import { Cpu } from 'lucide-react';
import { useModelInfo } from '../../hooks/useApi';
import { Skeleton } from '../../components/ui/Skeleton';

export default function ModelInsights() {
  const { data: modelInfo, isLoading } = useModelInfo();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Insights</h1>
        <p className="text-gray-400 mt-1">Understand how the AI makes its predictions</p>
      </div>
      <div className="glass-panel rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Cpu className="w-6 h-6 text-f1-red" />
          Active Model Metadata
        </h2>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-1/3" />
            <Skeleton className="h-8 w-1/2" />
            <Skeleton className="h-8 w-1/4" />
          </div>
        ) : (
          <div className="space-y-4 font-mono">
            <div className="flex justify-between py-2 border-b border-f1-border">
              <span className="text-gray-400">Model Type</span>
              <span className="text-white">{modelInfo?.model_type || 'Unknown'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-f1-border">
              <span className="text-gray-400">Features Used</span>
              <div className="flex gap-2 flex-wrap justify-end">
                {modelInfo?.features?.map((f: string) => (
                  <span key={f} className="bg-f1-border px-2 py-1 rounded text-xs">{f}</span>
                )) || 'None'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
