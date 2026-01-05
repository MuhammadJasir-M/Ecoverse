import React from "react";
import { Building2, Users, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";

const RoleSelection = () => {
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    if (role === "public") {
      navigate("/public");
    } else if (role === "government") {
      navigate("/government/login");
    } else if (role === "vendor") {
      navigate("/vendor/login");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl flex items-center justify-center shadow-lg mx-auto mb-6">
            <Building2 className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-3">
            Procurement Transparency Platform
          </h1>
          <p className="text-lg text-gray-600">
            Select your role to continue
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Government Portal */}
          <button
            onClick={() => handleRoleSelect("government")}
            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 text-left hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Government
            </h2>
            <p className="text-gray-600 mb-4">
              Create tenders, review bids, and award contracts
            </p>
            <div className="text-blue-600 font-medium group-hover:text-blue-700">
              Access Portal →
            </div>
          </button>

          {/* Vendor Portal */}
          <button
            onClick={() => handleRoleSelect("vendor")}
            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 text-left hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Vendor
            </h2>
            <p className="text-gray-600 mb-4">
              Browse tenders, submit bids, and track your proposals
            </p>
            <div className="text-green-600 font-medium group-hover:text-green-700">
              Access Portal →
            </div>
          </button>

          {/* Public Portal */}
          <button
            onClick={() => handleRoleSelect("public")}
            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 text-left hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Eye className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Public
            </h2>
            <p className="text-gray-600 mb-4">
              View awarded contracts, transparency data, and provide feedback
            </p>
            <div className="text-purple-600 font-medium group-hover:text-purple-700">
              View Portal →
            </div>
          </button>
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>AI-Assisted • Blockchain-Enabled • Public Accountability</p>
        </div>
      </div>
    </div>
  );
};

export default RoleSelection;




