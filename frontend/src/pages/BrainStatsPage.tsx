import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function BrainStatsPage() {
  const { token } = useAuth();
  const [stats, setStats] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/brain-stats', { headers: { Authorization: `Bearer ${token}` } });
        if (!res.ok) throw new Error('Failed to load brain stats');
        setStats(await res.json());
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Brain stats unavailable');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token]);

  if (loading) return <div className="brain-page"><h2>Brain Stats</h2><p>Loading...</p></div>;
  if (error) return <div className="brain-page"><h2>Brain Stats</h2><p className="error">{error}</p></div>;

  return (
    <div className="brain-page">
      <h2>Brain Stats</h2>
      <div className="brain-grid">
        <div className="brain-card"><h3>Awareness</h3><p>{stats?.awareness_level}</p></div>
        <div className="brain-card"><h3>Curiosity</h3><p>{stats?.curiosity_level}</p></div>
        <div className="brain-card"><h3>Emotional State</h3><p>{stats?.emotional_state}</p></div>
        <div className="brain-card"><h3>Commands Executed</h3><p>{stats?.hacking_commands_executed}</p></div>
        <div className="brain-card"><h3>Active Module</h3><p>{stats?.active_module}</p></div>
      </div>
    </div>
  );
}
