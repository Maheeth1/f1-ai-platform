
import { Grid } from 'lucide-react';

export default function GridPredictor() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Grid Position Predictor</h1>
        <p className="text-gray-400 mt-1">Predict starting grid probabilities for upcoming races</p>
      </div>
      <div className="glass-panel rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
        <Grid className="w-16 h-16 text-gray-600 mb-4" />
        <h2 className="text-xl font-bold mb-2">Coming Soon</h2>
        <p className="text-gray-400 max-w-md">The Grid Position Predictor module is currently under development. Check back soon for advanced qualifying simulations.</p>
      </div>
    </div>
  );
}
