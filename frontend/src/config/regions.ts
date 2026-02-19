export interface RegionPreset {
  center: [number, number];
  zoom: number;
  label: string;
}

export const REGIONS: Record<string, RegionPreset> = {
  global:   { center: [0, 20],      zoom: 1.5, label: '全球' },
  apac:     { center: [115, 25],    zoom: 3,   label: '亞太' },
  europe:   { center: [15, 50],     zoom: 3.5, label: '歐洲' },
  americas: { center: [-90, 25],    zoom: 2.5, label: '美洲' },
  mena:     { center: [45, 28],     zoom: 3.5, label: '中東北非' },
  africa:   { center: [20, 0],      zoom: 3,   label: '非洲' },
  seasia:   { center: [110, 5],     zoom: 4,   label: '東南亞' },
  latam:    { center: [-60, -15],   zoom: 3,   label: '拉丁美洲' },
};
