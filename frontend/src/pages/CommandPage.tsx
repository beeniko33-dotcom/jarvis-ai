import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function CommandPage() {
  const { token } = useAuth();
  const [command, setCommand] = useState('');
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ command }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Command failed' }));
        throw new Error(err.detail || 'Command failed');
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Command failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="command-page">
      <h2>Command Console</h2>
      <div className="command-form">
        <input type="text" value={command} onChange={e => setCommand(e.target.value)} placeholder="Command" />
        <button onClick={run} disabled={loading}>{loading ? 'Running...' : 'Run'}</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="command-result">
          <h3>Output</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
