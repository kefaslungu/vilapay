import { createBrowserRouter, Navigate } from 'react-router-dom'
import AuthLayout from '@/components/layout/AuthLayout'
import ProtectedLayout from '@/components/layout/ProtectedLayout'
import AppLayout from '@/components/layout/AppLayout'

import OnboardingPage from '@/pages/onboarding/OnboardingPage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import GroupDetailPage from '@/pages/groups/GroupDetailPage'
import JoinOrCreatePage from '@/pages/groups/JoinOrCreatePage'
import HistoryPage from '@/pages/history/HistoryPage'
import ProfilePage from '@/pages/profile/ProfilePage'
import NotFoundPage from '@/pages/not-found/NotFoundPage'

export const router = createBrowserRouter([
  // Onboarding (no auth, no bottom nav)
  {
    path: '/welcome',
    element: <OnboardingPage />,
  },

  // Auth routes (redirects to dashboard if already logged in)
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },

  // Protected routes (redirect to login if not authenticated)
  {
    element: <ProtectedLayout />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/groups/:id', element: <GroupDetailPage /> },
          { path: '/groups/new', element: <JoinOrCreatePage /> },
          { path: '/history', element: <HistoryPage /> },
          { path: '/profile', element: <ProfilePage /> },
        ],
      },
    ],
  },

  // Root redirect
  { path: '/', element: <Navigate to="/welcome" replace /> },

  // 404
  { path: '*', element: <NotFoundPage /> },
])
