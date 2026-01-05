import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { healthCheck } from "./services/api";

// Pages
import RoleSelection from "./pages/RoleSelection";
import GovernmentLogin from "./pages/GovernmentLogin";
import VendorLogin from "./pages/VendorLogin";
import VendorRegister from "./pages/VendorRegister";
import GovDashboard from "./pages/GovDashboard";
import VendorDashboard from "./pages/VendorDashboard";
import PublicDashboard from "./pages/PublicDashboard";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const { user, loading } = useAuth();
  const [apiStatus, setApiStatus] = React.useState("checking");

  useEffect(() => {
    // Check API health on mount
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      await healthCheck();
      setApiStatus("healthy");
      console.log("✅ Backend API is healthy");
    } catch (error) {
      setApiStatus("unhealthy");
      console.error("❌ Backend API is not responding:", error.message);
    }
  };

  // Show loading state while checking auth
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        {/* API Status Indicator - Only show on role selection */}
        {!user && (
          <div className="fixed top-4 right-4 z-50">
            <div
              className={`px-4 py-2 rounded-lg shadow-lg text-sm font-medium ${
                apiStatus === "healthy"
                  ? "bg-green-100 text-green-800"
                  : apiStatus === "unhealthy"
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {apiStatus === "checking"
                ? "Checking API..."
                : apiStatus === "healthy"
                ? "✓ API Online"
                : "✗ API Offline"}
            </div>
          </div>
        )}

        <Routes>
          {/* Role Selection - Entry Point */}
          <Route
            path="/"
            element={
              user ? (
                <Navigate
                  to={
                    user.role === "government"
                      ? "/government"
                      : user.role === "vendor"
                      ? "/vendor"
                      : "/public"
                  }
                  replace
                />
              ) : (
                <RoleSelection />
              )
            }
          />

          {/* Authentication Routes */}
          <Route
            path="/government/login"
            element={
              user?.role === "government" ? (
                <Navigate to="/government" replace />
              ) : (
                <GovernmentLogin />
              )
            }
          />
          <Route
            path="/vendor/login"
            element={
              user?.role === "vendor" ? (
                <Navigate to="/vendor" replace />
              ) : (
                <VendorLogin />
              )
            }
          />
          <Route
            path="/vendor/register"
            element={
              user?.role === "vendor" ? (
                <Navigate to="/vendor" replace />
              ) : (
                <VendorRegister />
              )
            }
          />

          {/* Protected Dashboard Routes */}
          <Route
            path="/government"
            element={
              <ProtectedRoute requiredRole="government" redirectTo="/government/login">
                <GovDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vendor"
            element={
              <ProtectedRoute requiredRole="vendor" redirectTo="/vendor/login">
                <VendorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/public"
            element={
              <ProtectedRoute requiredRole="public">
                <PublicDashboard />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to role selection */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
