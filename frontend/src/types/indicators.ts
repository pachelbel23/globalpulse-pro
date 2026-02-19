export interface IndicatorPoint {
  date: string;
  value: number | null;
}

export interface IndicatorSeries {
  series_id: string;
  title: string;
  units: string;
  frequency: string;
  data: IndicatorPoint[];
}
