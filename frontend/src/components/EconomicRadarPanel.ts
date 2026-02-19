import { Panel } from './Panel';
import { api } from '@/services/api-client';
import { formatNumber, formatPercent } from '@/utils/format';
import type { IndicatorSeries } from '@/types/indicators';

const TRACKED_SERIES = [
  { id: 'GDP', label: 'GDP' },
  { id: 'CPIAUCSL', label: 'CPI' },
  { id: 'UNRATE', label: '失業率' },
  { id: 'FEDFUNDS', label: '聯邦基金利率' },
];

export class EconomicRadarPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor(container: HTMLElement) {
    super(container, '實體經濟雷達');
    this.loadData();
    this.refreshTimer = setInterval(() => this.loadData(), 15 * 60 * 1000);
  }

  private async loadData(): Promise<void> {
    this.body.innerHTML = '<div class="loading">Loading indicators...</div>';
    const rows: string[] = [];

    for (const { id, label } of TRACKED_SERIES) {
      try {
        const series = await api.getFredSeries(id);
        rows.push(this.renderRow(label, series));
      } catch {
        rows.push(`<div class="indicator-row error">${label}: unavailable</div>`);
      }
    }

    this.body.innerHTML = rows.join('');
  }

  private renderRow(label: string, series: IndicatorSeries): string {
    const latest = series.data[series.data.length - 1];
    const prev = series.data[series.data.length - 2];

    if (!latest) return `<div class="indicator-row">${label}: no data</div>`;

    let changeHtml = '';
    if (prev && latest.value != null && prev.value != null) {
      const change = ((latest.value - prev.value) / Math.abs(prev.value)) * 100;
      const cls = change >= 0 ? 'positive' : 'negative';
      changeHtml = `<span class="change ${cls}">${formatPercent(change)}</span>`;
    }

    return `
      <div class="indicator-row">
        <span class="indicator-label">${label}</span>
        <span class="indicator-value">${formatNumber(latest.value ?? 0)}</span>
        ${changeHtml}
      </div>
    `;
  }

  update(_data: unknown): void {
    this.loadData();
  }

  destroy(): void {
    if (this.refreshTimer) clearInterval(this.refreshTimer);
    super.destroy();
  }
}
