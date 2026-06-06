import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './components/layout/AppLayout';

// Lazy load pages for performance
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const LapTimePredictor = React.lazy(() => import('./pages/LapTimePredictor'));
const GridPredictor = React.lazy(() => import('./pages/GridPredictor'));
const RaceSimulation = React.lazy(() => import('./pages/RaceSimulation'));
const CircuitIntelligence = React.lazy(() => import('./pages/CircuitIntelligence'));
const DriverAnalysis = React.lazy(() => import('./pages/DriverAnalysis'));
const ModelInsights = React.lazy(() => import('./pages/ModelInsights'));
const Settings = React.lazy(() => import('./pages/Settings'));

import { LoadingSpinner } from './components/ui/LoadingSpinner';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout>
          <React.Suspense fallback={<div className="h-full w-full flex items-center justify-center"><LoadingSpinner /></div>}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/lap-time" element={<LapTimePredictor />} />
              <Route path="/grid" element={<GridPredictor />} />
              <Route path="/simulation" element={<RaceSimulation />} />
              <Route path="/circuits" element={<CircuitIntelligence />} />
              <Route path="/drivers" element={<DriverAnalysis />} />
              <Route path="/insights" element={<ModelInsights />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </React.Suspense>
        </AppLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
