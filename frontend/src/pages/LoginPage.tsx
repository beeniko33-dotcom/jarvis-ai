import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login, register, isLoading, error } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isRegister) {
        await register({ username, password });
      } else {
        await login({ username, password });
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>{isRegister ? 'Create Account' : 'Sign In'}</h2>
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
        {error && <p className="auth-error">{error}</p>}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Please wait...' : isRegister ? 'Register' : 'Login'}
        </button>
        <button type="button" className="link-btn" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? 'Already have an account? Sign in' : 'Need an account? Register'}
        </button>
      </form>
    </div>
  );
}
