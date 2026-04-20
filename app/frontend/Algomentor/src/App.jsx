import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './layout/MainLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ProblemWorkspacePage from './pages/ProblemWorkspacePage';
import SimulationPage from './pages/SimulationPage';
import SolutionReviewPage from './pages/SolutionReviewPage';
import ProblemsListPage from './pages/ProblemsListPage';
import React, { Suspense } from "react";

const AvatarBuilder = React.lazy(() =>
  import("./layout/AvatarBuilder")
);


// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/" replace />;
};

// Public Route wrapper (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
      path="/avatar"
      element={
      <Suspense fallback={<div>Loading Avatar Studio...</div>}>
        <AvatarBuilder />
      </Suspense>}
      />
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/problems" element={<ProblemsListPage />} />
        <Route path="/problems/workspace/:problemId" element={<ProblemWorkspacePage />} />
        <Route path="/simulation" element={<SimulationPage />} />
        <Route path="/solution-review" element={<SolutionReviewPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;