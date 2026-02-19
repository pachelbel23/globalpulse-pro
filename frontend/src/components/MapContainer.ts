import maplibregl from 'maplibre-gl';
import { Deck, type Layer, type LayersList } from '@deck.gl/core';
import { REGIONS } from '@/config/regions';

export class MapContainer {
  private map: maplibregl.Map | null = null;
  private deck: Deck | null = null;
  private container: HTMLElement;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container #${containerId} not found`);
    this.container = el;
  }

  init(): void {
    this.map = new maplibregl.Map({
      container: this.container as HTMLDivElement,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: REGIONS.global.center,
      zoom: REGIONS.global.zoom,
      pitch: 45,
      bearing: 0,
      antialias: true,
    });

    this.deck = new Deck({
      parent: this.container as HTMLDivElement,
      viewState: {
        longitude: REGIONS.global.center[0],
        latitude: REGIONS.global.center[1],
        zoom: REGIONS.global.zoom,
        pitch: 45,
        bearing: 0,
      },
      controller: true,
      layers: [],
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      onViewStateChange: ({ viewState }: any) => {
        this.map?.jumpTo({
          center: [viewState.longitude, viewState.latitude],
          zoom: viewState.zoom,
          pitch: viewState.pitch,
          bearing: viewState.bearing,
        });
      },
    });
  }

  flyTo(regionKey: string): void {
    const region = REGIONS[regionKey];
    if (!region || !this.deck) return;

    this.deck.setProps({
      viewState: {
        longitude: region.center[0],
        latitude: region.center[1],
        zoom: region.zoom,
        pitch: 45,
        bearing: 0,
        transitionDuration: 2000,
      },
    });
  }

  updateLayers(layers: (Layer | null | undefined | false)[]): void {
    this.deck?.setProps({ layers });
  }

  destroy(): void {
    this.deck?.finalize();
    this.map?.remove();
  }
}
