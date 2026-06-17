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
import PortfolioPage from './pages/PortfolioPage';
import SignalPage from './pages/SignalPage';
import RiskPage from './pages/RiskPage';
import ExchangePage from './pages/ExchangePage';
import CommandPage from './pages/CommandPage';
import BrainStatsPage from './pages/BrainStatsPage';

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
      { path: 'portfolio', element: <PortfolioPage /> },
      { path: 'signal', element: <SignalPage /> },
      { path: 'risk', element: <RiskPage /> },
      { path: 'exchange', element: <ExchangePage /> },
      { path: 'command', element: <CommandPage /> },
      { path: 'brain', element: <BrainStatsPage /> },
      { path: 'diagnostic', element: <DiagnosticPage /> },
    ],
  },
]);
