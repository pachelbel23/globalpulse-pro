import './styles/main.css';
import { App } from '@/App';

const root = document.getElementById('app');
if (root) {
  root.innerHTML = `
    <div id="toolbar" class="toolbar">
      <span class="logo">Global Pulse Pro</span>
    </div>
    <div id="map-container" class="map-container"></div>
    <div id="side-panel" class="side-panel"></div>
  `;

  const app = new App('app');
  app.init();
}
