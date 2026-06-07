import { api } from './api';
import type { PredictionRequest, PredictionResponse, ModelRegistryResponse } from '../types';

export const endpoints = {
  health: async () => {
    const { data } = await api.get('/health');
    return data;
  },
  modelInfo: async (target: string) => {
    const { data } = await api.get(`/models/info/${target}`);
    return data;
  },
  sampleRequest: async () => {
    const { data } = await api.get('/sample-request');
    return data;
  },
  predict: async (target: string, payload: PredictionRequest) => {
    const { data } = await api.post<PredictionResponse>(`/${target}/predict`, payload);
    return data;
  },
  getModels: async () => {
    const { data } = await api.get<ModelRegistryResponse>('/models/');
    return data;
  },
  getActiveModels: async () => {
    const { data } = await api.get('/models/active');
    return data;
  }
};
