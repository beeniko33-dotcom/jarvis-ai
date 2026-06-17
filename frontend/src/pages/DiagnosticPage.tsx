import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface DiagnosticData {
  status: string;
  service: string;
  domain: string;
  consciousness: any;
  diagnostics?: {
    cpu_percent: number;
    memory_percent: number;
    boot_time: string;
  };
}

export default function DiagnosticPage() {
  const { token } = useAuth();
  const [data, setData] = useState<DiagnosticData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/diagnostic', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to load diagnostics');
        const json = await res.json();
        setData(json as DiagnosticData);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Diagnostics unavailable');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token]);

  if (loading) return <div className="diagnostic-page"><h2>Diagnostics</h2><p>Loading...</p></div>;
  if (error) return <div className="diagnostic-page"><h2>Diagnostics</h2><p className="error">{error}</p></div>;

  return (
    <div className="diagnostic-page">
      <h2>Diagnostics</h2>
      <div className="diagnostic-grid">
        <div className="diagnostic-card">
          <h3>Service</h3>
          <p><strong>Status:</strong> {data?.status}</p>
          <p><strong>Service:</strong> {data?.service}</p>
          <p><strong>Domain:</strong> {data?.domain}</p>
        </div>
        {data?.diagnostics && (
          <div className="diagnostic-card">
            <h3>System</h3>
            <p><strong>CPU:</strong> {data.diagnostics.cpu_percent}%</p>
            <p><strong>Memory:</strong> {data.diagnostics.memory_percent}%</p>
            <p><strong>Boot Time:</strong> {data.diagnostics.boot_time}</p>
          </div>
        )}
        <div className="diagnostic-card">
          <h3>Consciousness</h3>
          <pre>{JSON.stringify(data?.consciousness ?? {}, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
