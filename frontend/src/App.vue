<script setup lang="ts">
import { onMounted } from 'vue';
import { useTelemetryStore } from './stores/telemetry';

const store = useTelemetryStore();

onMounted(async () => {
  await store.fetchInitialData();
  store.connectWebSocket();
});
</script>

<template>
  <div style="min-height: 100vh; display: flex; flex-direction: column;">
    <!-- Top Header -->
    <header style="background: #111827; border-bottom: 1px solid #1f2937; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 10px #38bdf8;"></span>
        <h1 style="margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.025em; color: #f8fafc;">
          THERMOGREK <span style="font-weight: 400; font-size: 0.875rem; color: #94a3b8; margin-left: 8px;">Thermal Utility Plant Monitoring</span>
        </h1>
      </div>
      <div style="display: flex; align-items: center; gap: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem;">
        <span :style="{ color: store.isWsConnected ? '#4ade80' : '#f87171', display: 'flex', alignItems: 'center', gap: '6px' }">
          ● {{ store.isWsConnected ? 'LIVE STREAM CONNECTED' : 'STREAM DISCONNECTED' }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main style="padding: 24px; max-width: 1400px; margin: 0 auto; width: 100%; box-sizing: border-box;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 24px;">
        
        <!-- HE-01 Card -->
        <div style="background: #1e293b; border-radius: 8px; border: 1px solid #334155; padding: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="margin: 0; font-size: 1.1rem; color: #e2e8f0;">HE-01 (Heat Exchanger)</h2>
            <span :style="{
              padding: '4px 10px',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: '600',
              background: store.assets['HE-01']?.health_status === 'CRITICAL' ? '#7f1d1d' : store.assets['HE-01']?.health_status === 'WARNING' ? '#78350f' : '#14532d',
              color: store.assets['HE-01']?.health_status === 'CRITICAL' ? '#fca5a5' : store.assets['HE-01']?.health_status === 'WARNING' ? '#fcd34d' : '#86efac'
            }">
              {{ store.assets['HE-01']?.health_status || 'UNKNOWN' }}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-family: 'JetBrains Mono', monospace;">
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">PRESSURE DROP (&Delta;P)</span>
              <span style="font-size: 1.25rem; font-weight: 700; color: #38bdf8;">
                {{ store.assets['HE-01']?.kpis?.delta_p_bar != null ? store.assets['HE-01']?.kpis?.delta_p_bar + ' bar' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">HEAT DUTY (Q)</span>
              <span style="font-size: 1.25rem; font-weight: 700; color: #f59e0b;">
                {{ store.assets['HE-01']?.kpis?.heat_duty_kw != null ? store.assets['HE-01']?.kpis?.heat_duty_kw + ' kW' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">DELTA T (HOT)</span>
              <span style="font-size: 1.25rem; font-weight: 700; color: #e2e8f0;">
                {{ store.assets['HE-01']?.kpis?.delta_t_c != null ? store.assets['HE-01']?.kpis?.delta_t_c + ' °C' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">HEALTH INDEX</span>
              <span style="font-size: 1.25rem; font-weight: 700;" :style="{ color: (store.assets['HE-01']?.kpis?.health_index_pct ?? 100) < 65 ? '#ef4444' : '#22c55e' }">
                {{ store.assets['HE-01']?.kpis?.health_index_pct != null ? store.assets['HE-01']?.kpis?.health_index_pct + ' %' : '--' }}
              </span>
            </div>
          </div>
        </div>

        <!-- CT-01 Card -->
        <div style="background: #1e293b; border-radius: 8px; border: 1px solid #334155; padding: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="margin: 0; font-size: 1.1rem; color: #e2e8f0;">CT-01 (Cooling Tower)</h2>
            <span :style="{
              padding: '4px 10px',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: '600',
              background: store.assets['CT-01']?.health_status === 'CRITICAL' ? '#7f1d1d' : store.assets['CT-01']?.health_status === 'WARNING' ? '#78350f' : '#14532d',
              color: store.assets['CT-01']?.health_status === 'CRITICAL' ? '#fca5a5' : store.assets['CT-01']?.health_status === 'WARNING' ? '#fcd34d' : '#86efac'
            }">
              {{ store.assets['CT-01']?.health_status || 'UNKNOWN' }}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-family: 'JetBrains Mono', monospace;">
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">APPROACH TEMP</span>
              <span style="font-size: 1.25rem; font-weight: 700; color: #38bdf8;">
                {{ store.assets['CT-01']?.kpis?.approach_temp_c != null ? store.assets['CT-01']?.kpis?.approach_temp_c + ' °C' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">EFFECTIVENESS</span>
              <span style="font-size: 1.25rem; font-weight: 700; color: #3b82f6;">
                {{ store.assets['CT-01']?.kpis?.effectiveness_pct != null ? store.assets['CT-01']?.kpis?.effectiveness_pct + ' %' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">HEALTH INDEX</span>
              <span style="font-size: 1.25rem; font-weight: 700;" :style="{ color: (store.assets['CT-01']?.kpis?.health_index_pct ?? 100) < 65 ? '#ef4444' : '#22c55e' }">
                {{ store.assets['CT-01']?.kpis?.health_index_pct != null ? store.assets['CT-01']?.kpis?.health_index_pct + ' %' : '--' }}
              </span>
            </div>
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #1e293b;">
              <span style="color: #94a3b8; font-size: 0.75rem; display: block;">LAST UPDATE</span>
              <span style="font-size: 0.85rem; font-weight: 500; color: #94a3b8;">
                {{ store.lastHeartbeat ? store.lastHeartbeat.toLocaleTimeString() : 'Waiting...' }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>
