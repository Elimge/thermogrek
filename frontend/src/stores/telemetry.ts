import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { AssetLatestData, AssetMeta } from '../types/telemetry';

export const useTelemetryStore = defineStore('telemetry', () => {
  const assets = ref<Record<string, AssetLatestData>>({});
  const assetList = ref<AssetMeta[]>([]);
  const isWsConnected = ref<boolean>(false);
  const lastHeartbeat = ref<Date | null>(null);

  let socket: WebSocket | null = null;
  let reconnectTimer: any = null;

  async function fetchInitialData() {
    try {
      const res = await fetch('http://127.0.0.1:8001/api/v1/assets');
      if (res.ok) {
        assetList.value = await res.json();
      }

      for (const asset of assetList.value) {
        const latestRes = await fetch(`http://127.0.0.1:8001/api/v1/assets/${asset.id}/latest`);
        if (latestRes.ok) {
          const data: AssetLatestData = await latestRes.json();
          assets.value[asset.id] = data;
        }
      }
    } catch (err) {
      console.error('Failed to fetch initial asset state:', err);
    }
  }

  function connectWebSocket() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    socket = new WebSocket('ws://127.0.0.1:8001/ws/telemetry');

    socket.onopen = () => {
      isWsConnected.value = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'KPI_UPDATE' && msg.data) {
          const kpiPayload = msg.data;
          const assetId = kpiPayload.asset_id;

          if (!assets.value[assetId]) {
            assets.value[assetId] = {
              asset_id: assetId,
              timestamp: kpiPayload.timestamp,
              metrics: {},
              kpis: kpiPayload,
              health_status: kpiPayload.health_status || 'NORMAL'
            };
          } else {
            assets.value[assetId].kpis = kpiPayload;
            assets.value[assetId].health_status = kpiPayload.health_status || assets.value[assetId].health_status;
            assets.value[assetId].timestamp = kpiPayload.timestamp;
          }
          lastHeartbeat.value = new Date();
        }
      } catch (e) {
        console.error('Error parsing live WS telemetry frame:', e);
      }
    };

    socket.onclose = () => {
      isWsConnected.value = false;
      reconnectTimer = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };

    socket.onerror = () => {
      socket?.close();
    };
  }

  return {
    assets,
    assetList,
    isWsConnected,
    lastHeartbeat,
    fetchInitialData,
    connectWebSocket
  };
});
