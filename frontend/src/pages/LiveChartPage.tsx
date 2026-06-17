import { useEffect, useRef } from 'react';

export default function LiveChartPage() {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.event === 'price') {
          console.log('live price', msg);
        }
      } catch {
        // ignore non-JSON messages
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  return (
    <div className="live-chart-page">
      <h2>Live Price Stream</h2>
      <p className="muted">Connects to the shared WebSocket and streams price ticks below.</p>
    </div>
  );
}
