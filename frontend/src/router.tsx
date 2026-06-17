import { createBrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import AppLayout from './layouts/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import BacktesterPage from './pages/BacktesterPage';
import OnboardingPage from './pages/OnboardingPage';

export const router = createBrowserRouter([
  {
    element: <AuthProvider><AppLayout /></AuthProvider>,
    children: [
      { index: true, element: <LoginPage /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'backtest', element: <BacktesterPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'onboarding', element: <OnboardingPage /> },
    ],
  },
]);
