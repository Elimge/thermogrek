export interface HeatExchangerMetrics {
  t_hot_in_c: number;
  t_hot_out_c: number;
  t_cold_in_c: number;
  t_cold_out_c: number;
  p_in_bar: number;
  p_out_bar: number;
  flow_rate_m3h: number;
  u_effective?: number;
  heat_duty_kw?: number;
}

export interface CoolingTowerMetrics {
  t_water_in_c: number;
  t_water_out_c: number;
  t_ambient_db_c: number;
  relative_humidity_pct: number;
  fan_speed_rpm: number;
  water_flow_m3h: number;
  t_wet_bulb_c?: number;
  actual_approach_c?: number;
}

export interface ThermodynamicKPIs {
  delta_t_c?: number;
  delta_p_bar?: number;
  heat_duty_kw?: number;
  approach_temp_c?: number;
  effectiveness_pct?: number;
  health_index_pct: number;
  health_status: 'NORMAL' | 'WARNING' | 'CRITICAL';
  alarm_triggered?: {
    severity: string;
    alarm_code: string;
    message: string;
  };
}

export interface AssetLatestData {
  asset_id: string;
  timestamp: string;
  metrics: HeatExchangerMetrics | CoolingTowerMetrics | Record<string, any>;
  kpis: ThermodynamicKPIs;
  health_status: 'NORMAL' | 'WARNING' | 'CRITICAL';
}

export interface AssetMeta {
  id: string;
  name: string;
  asset_type: 'SHELL_TUBE_HE' | 'COOLING_TOWER';
  health_status: 'NORMAL' | 'WARNING' | 'CRITICAL';
}
