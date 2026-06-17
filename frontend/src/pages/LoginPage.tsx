import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login, register, isLoading, error, brokerConnect } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [brokerMode, setBrokerMode] = useState(false);
  const [brokerType, setBrokerType] = useState('MCL');
  const [brokerUsername, setBrokerUsername] = useState('');
  const [brokerPassword, setBrokerPassword] = useState('');
  const [brokerServer, setBrokerServer] = useState('');

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (brokerMode) {
      try {
        await brokerConnect({
          broker: brokerType,
          username: brokerUsername,
          password: brokerPassword,
          server: brokerServer || undefined,
        });
      } catch (err) {
        console.error(err);
      }
    } else if (isRegister) {
      try {
        await register({ username, password });
      } catch (err) {
        console.error(err);
      }
    } else {
      try {
        await login({ username, password });
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleAuth}>
        <h2>{brokerMode ? 'Broker MCL Login' : isRegister ? 'Create Account' : 'Sign In'}</h2>

        {brokerMode ? (
          <>
            <select value={brokerType} onChange={e => setBrokerType(e.target.value)}>
              <option value="MCL">MCL</option>
              <option value="MT4">MT4</option>
              <option value="MT5">MT5</option>
              <option value="DERIV">DERIV</option>
            </select>
            <input
              type="text"
              placeholder="Broker Username"
              value={brokerUsername}
              onChange={e => setBrokerUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Broker Password"
              value={brokerPassword}
              onChange={e => setBrokerPassword(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Server (optional)"
              value={brokerServer}
              onChange={e => setBrokerServer(e.target.value)}
            />
          </>
        ) : (
          <>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </>
        )}

        {error && <p className="auth-error">{error}</p>}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Please wait...' : brokerMode ? 'Connect Broker' : isRegister ? 'Register' : 'Login'}
        </button>
        <button type="button" className="link-btn" onClick={() => setBrokerMode(!brokerMode)}>
          {brokerMode ? 'Use platform login' : 'Connect with Broker'}
        </button>
        {!brokerMode && (
          <button type="button" className="link-btn" onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Already have an account? Sign in' : 'Need an account? Register'}
          </button>
        )}
      </form>
    </div>
  );
}
