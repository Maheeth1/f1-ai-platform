export interface Driver {
  code: number;
  name: string;
  team: string;
  number: number;
}

export interface PredictionRequest {
  Driver: string;
  LapNumber?: number;
  TyreLife?: number;
}

export interface PredictionResponse {
  prediction: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
  confidence_report: Record<string, any>;
  model_version: string;
  latency_ms: number;
}

export interface ModelVersionInfo {
  version: string;
  path: string;
  registered_at: string;
  metrics: Record<string, any>;
  metadata: Record<string, any>;
}

export interface TargetRegistryInfo {
  active_version: string | null;
  versions: ModelVersionInfo[];
}

export interface ModelRegistryResponse {
  laptime?: TargetRegistryInfo;
  gridposition?: TargetRegistryInfo;
  simulation?: TargetRegistryInfo;
  [key: string]: TargetRegistryInfo | undefined;
}
