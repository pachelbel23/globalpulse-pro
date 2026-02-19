import { Panel } from './Panel';
import { api } from '@/services/api-client';

export class AuditPanel extends Panel {
  constructor(container: HTMLElement) {
    super(container, 'AI 商模審計器');
    this.renderForm();
  }

  private renderForm(): void {
    this.body.innerHTML = `
      <form class="audit-form">
        <label>商業模式描述
          <textarea name="model_description" rows="3" placeholder="例：DTC 運動鞋品牌，透過電商直銷..."></textarea>
        </label>
        <label>目標市場
          <input name="target_market" placeholder="例：越南" />
        </label>
        <label>產業
          <input name="industry" placeholder="例：消費零售" />
        </label>
        <button type="submit">分析 SWOT</button>
      </form>
      <div class="audit-result"></div>
    `;

    this.body.querySelector('form')!.addEventListener('submit', (e) => {
      e.preventDefault();
      this.runAudit();
    });
  }

  private async runAudit(): Promise<void> {
    const form = this.body.querySelector('form')! as HTMLFormElement;
    const fd = new FormData(form);
    const resultEl = this.body.querySelector('.audit-result')!;

    resultEl.innerHTML = '<div class="loading">AI 分析中...</div>';

    try {
      const report = await api.postAudit({
        model_description: fd.get('model_description') as string,
        target_market: fd.get('target_market') as string,
        industry: fd.get('industry') as string,
      });

      resultEl.innerHTML = this.renderSWOT(report);
    } catch (err) {
      resultEl.innerHTML = `<div class="error">分析失敗: ${err}</div>`;
    }
  }

  private renderSWOT(report: Record<string, unknown>): string {
    const sections = [
      { key: 'strengths', label: '優勢 (S)', cls: 'success' },
      { key: 'weaknesses', label: '劣勢 (W)', cls: 'warning' },
      { key: 'opportunities', label: '機會 (O)', cls: 'accent' },
      { key: 'threats', label: '威脅 (T)', cls: 'danger' },
    ];

    let html = '';
    for (const { key, label, cls } of sections) {
      const items = report[key] as string[] | undefined;
      if (!items) continue;
      html += `
        <div class="swot-section ${cls}">
          <h4>${label}</h4>
          <ul>${items.map((i) => `<li>${i}</li>`).join('')}</ul>
        </div>
      `;
    }

    if (report['risk_summary']) {
      html += `<div class="risk-summary"><strong>風險摘要:</strong> ${report['risk_summary']}</div>`;
    }

    return html;
  }

  update(_data: unknown): void {}
}
