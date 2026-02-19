import { REGIONS } from '@/config/regions';

export function getActiveRegion(): string {
  const hour = new Date().getUTCHours();

  if (hour >= 0 && hour < 8) return 'apac';      // UTC+8~+12 trading
  if (hour >= 7 && hour < 16) return 'europe';    // UTC+0~+3 trading
  if (hour >= 13 && hour < 22) return 'americas'; // UTC-5~-8 trading
  return 'global';
}

export class TimezoneFocus {
  private timer: ReturnType<typeof setInterval> | null = null;
  private paused = false;
  private idleTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private onFocus: (region: string) => void) {}

  start(): void {
    this.apply();
    this.timer = setInterval(() => {
      if (!this.paused) this.apply();
    }, 5 * 60 * 1000); // check every 5 min
  }

  pause(): void {
    this.paused = true;
    if (this.idleTimer) clearTimeout(this.idleTimer);
    this.idleTimer = setTimeout(() => {
      this.paused = false;
    }, 10 * 60 * 1000); // resume after 10min idle
  }

  private apply(): void {
    this.onFocus(getActiveRegion());
  }

  stop(): void {
    if (this.timer) clearInterval(this.timer);
    if (this.idleTimer) clearTimeout(this.idleTimer);
  }
}
