import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
} from "react-router-dom";
import { Building2, Users, Eye, Activity } from "lucide-react";
import GovDashboard from "./pages/GovDashboard";
import VendorDashboard from "./pages/VendorDashboard";
import PublicDashboard from "./pages/PublicDashboard";
import { healthCheck } from "./services/api";

function App() {
  const [activePortal, setActivePortal] = useState("government");
  const [apiStatus, setApiStatus] = useState("checking");

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

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        {/* Header */}
        <header className="bg-white shadow-md border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link
                to="/"
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
                  <Building2 className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800 leading-tight">
                    Procurement Transparency Platform
                  </h1>
                  <p className="text-xs text-gray-500 font-medium">
                    AI-Assisted • Blockchain-Enabled • Public Accountability
                  </p>
                </div>
              </Link>

              {/* API Status Indicator */}
              <div className="flex items-center space-x-2">
                <Activity
                  className={`w-4 h-4 ${
                    apiStatus === "healthy" ? "text-green-500" : "text-red-500"
                  }`}
                />
                <span
                  className={`text-xs font-medium ${
                    apiStatus === "healthy" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {apiStatus === "checking"
                    ? "Checking..."
                    : apiStatus === "healthy"
                    ? "API Online"
                    : "API Offline"}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Portal Navigation */}
        <div className="bg-white border-b border-gray-200 shadow-sm">
          <div className="container mx-auto px-4">
            <div className="flex space-x-1 py-3">
              <Link
                to="/government"
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
                  activePortal === "government"
                    ? "bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg transform scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
                onClick={() => setActivePortal("government")}
              >
                <Building2 className="w-5 h-5" />
                <span>Government Portal</span>
              </Link>

              <Link
                to="/vendor"
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
                  activePortal === "vendor"
                    ? "bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg transform scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
                onClick={() => setActivePortal("vendor")}
              >
                <Users className="w-5 h-5" />
                <span>Vendor Portal</span>
              </Link>

              <Link
                to="/public"
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
                  activePortal === "public"
                    ? "bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg transform scale-105"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
                onClick={() => setActivePortal("public")}
              >
                <Eye className="w-5 h-5" />
                <span>Public Portal</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/government" replace />} />
            <Route path="/government" element={<GovDashboard />} />
            <Route path="/vendor" element={<VendorDashboard />} />
            <Route path="/public" element={<PublicDashboard />} />
            <Route path="*" element={<Navigate to="/government" replace />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
              <p>© 2026 Procurement Transparency Platform • VIT Hackathon</p>
              <div className="flex space-x-4 mt-2 md:mt-0">
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary-600"
                >
                  API Docs
                </a>
                <span>•</span>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary-600"
                >
                  GitHub
                </a>
                <span>•</span>
                <button
                  onClick={checkAPIHealth}
                  className="hover:text-primary-600"
                >
                  Check API
                </button>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
