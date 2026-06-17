import { createBrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import AppLayout from './layouts/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import BacktesterPage from './pages/BacktesterPage';
import OnboardingPage from './pages/OnboardingPage';
import LiveChartPage from './pages/LiveChartPage';
import MarketPage from './pages/MarketPage';
import TradePage from './pages/TradePage';
import DiagnosticPage from './pages/DiagnosticPage';

export const router = createBrowserRouter([
  {
    element: <AuthProvider><AppLayout /></AuthProvider>,
    children: [
      { index: true, element: <LoginPage /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'backtest', element: <BacktesterPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'onboarding', element: <OnboardingPage /> },
      { path: 'live', element: <LiveChartPage /> },
      { path: 'market', element: <MarketPage /> },
      { path: 'trade', element: <TradePage /> },
      { path: 'diagnostic', element: <DiagnosticPage /> },
    ],
  },
]);
