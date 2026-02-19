import { MapContainer } from '@/components/MapContainer';
import { EconomicRadarPanel } from '@/components/EconomicRadarPanel';
import { AuditPanel } from '@/components/AuditPanel';
import { TimezoneFocus } from '@/services/timezone-focus';

export class App {
  private map: MapContainer;
  private economicPanel: EconomicRadarPanel | null = null;
  private auditPanel: AuditPanel | null = null;
  private timezoneFocus: TimezoneFocus;

  constructor(_rootId: string) {
    this.map = new MapContainer('map-container');
    this.timezoneFocus = new TimezoneFocus((region) => this.map.flyTo(region));
  }

  init(): void {
    this.map.init();

    const sidePanel = document.getElementById('side-panel');
    if (sidePanel) {
      this.economicPanel = new EconomicRadarPanel(sidePanel);
      this.auditPanel = new AuditPanel(sidePanel);
    }

    this.timezoneFocus.start();

    // Pause auto-focus on manual map interaction
    document.getElementById('map-container')?.addEventListener('mousedown', () => {
      this.timezoneFocus.pause();
    });
  }

  destroy(): void {
    this.timezoneFocus.stop();
    this.economicPanel?.destroy();
    this.auditPanel?.destroy();
    this.map.destroy();
  }
}
