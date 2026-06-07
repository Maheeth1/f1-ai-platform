
import { Settings as SettingsIcon } from 'lucide-react';

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
        <p className="text-gray-400 mt-1">Configure platform preferences and API endpoints</p>
      </div>
      <div className="glass-panel rounded-xl p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
        <SettingsIcon className="w-16 h-16 text-gray-600 mb-4" />
        <h2 className="text-xl font-bold mb-2">Coming Soon</h2>
        <p className="text-gray-400 max-w-md">Configuration options for models and endpoints will be available in the next release.</p>
      </div>
    </div>
  );
}
