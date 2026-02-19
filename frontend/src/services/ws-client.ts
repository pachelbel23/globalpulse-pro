import type { WSMessage, WSSubscribe } from '@/types/api';

type MessageHandler = (msg: WSMessage) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string;

  constructor(url: string = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/live`) {
    this.url = url;
  }

  connect(): void {
    this.ws = new WebSocket(this.url);

    this.ws.onmessage = (event) => {
      const msg: WSMessage = JSON.parse(event.data);
      const channelHandlers = this.handlers.get(msg.channel);
      if (channelHandlers) {
        channelHandlers.forEach((h) => h(msg));
      }
    };

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(), 5000);
    };
  }

  subscribe(channel: string, handler: MessageHandler): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
    }
    this.handlers.get(channel)!.add(handler);

    if (this.ws?.readyState === WebSocket.OPEN) {
      const msg: WSSubscribe = { action: 'subscribe', channels: [channel] };
      this.ws.send(JSON.stringify(msg));
    }
  }

  unsubscribe(channel: string, handler: MessageHandler): void {
    this.handlers.get(channel)?.delete(handler);
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
  }
}
