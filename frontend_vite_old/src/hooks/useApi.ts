import { useQuery, useMutation } from '@tanstack/react-query';
import { endpoints } from '../services/endpoints';
import type { PredictionRequest } from '../types';

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: endpoints.health,
    refetchInterval: 30000, // Refetch every 30s
  });
};

export const useModelInfo = (target: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['modelInfo', target],
    queryFn: () => endpoints.modelInfo(target),
    enabled,
  });
};

export const useSampleRequest = () => {
  return useQuery({
    queryKey: ['sampleRequest'],
    queryFn: endpoints.sampleRequest,
    staleTime: Infinity,
  });
};

export const usePrediction = (target: string) => {
  return useMutation({
    mutationFn: (payload: PredictionRequest) => endpoints.predict(target, payload),
  });
};

export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: endpoints.getModels,
  });
};

export const useActiveModels = () => {
  return useQuery({
    queryKey: ['activeModels'],
    queryFn: endpoints.getActiveModels,
  });
};
