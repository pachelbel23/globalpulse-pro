export interface RiskScore {
  region_code: string;
  overall: number;
  breakdown: Record<string, number>;
}
