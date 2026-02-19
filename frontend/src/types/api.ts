export interface HealthResponse {
  status: string;
  version: string;
}

export interface WSMessage {
  channel: string;
  event: string;
  data: unknown;
  timestamp: string;
}

export interface WSSubscribe {
  action: 'subscribe' | 'unsubscribe';
  channels: string[];
}
