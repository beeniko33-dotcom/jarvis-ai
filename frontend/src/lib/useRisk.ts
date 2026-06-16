import { useState, useCallback } from 'react';
import type { PositionRiskRequest, RiskCheckResponse, UserRiskState } from '../types/risk';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useRisk() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkPosition = useCallback(async (req: PositionRiskRequest): Promise<RiskCheckResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/risk/check-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(req),
      });
      if (!res.ok) throw new Error('Risk check failed');
      return res.json();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Risk check failed');
      throw e;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const getUserRiskState = useCallback(async (userId: string): Promise<UserRiskState> => {
    const res = await fetch(`${API_URL}/risk/state/${encodeURIComponent(userId)}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load risk state');
    return res.json();
  }, [token]);

  return { checkPosition, getUserRiskState, loading, error };
}
