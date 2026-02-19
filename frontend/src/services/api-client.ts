import type { IndicatorSeries } from '@/types/indicators';
import type { HealthResponse } from '@/types/api';

const BASE_URL = import.meta.env.VITE_API_URL || '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${resp.statusText}`);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>('/api/health'),

  getFredSeries: (seriesId: string, start?: string, end?: string) => {
    const params = new URLSearchParams();
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    const qs = params.toString();
    return request<IndicatorSeries>(`/api/indicators/fred/${seriesId}${qs ? '?' + qs : ''}`);
  },

  postAudit: (body: { model_description: string; target_market: string; industry: string }) =>
    request<Record<string, unknown>>('/api/audit', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getScrapers: () => request<unknown[]>('/api/scrapers'),
};
