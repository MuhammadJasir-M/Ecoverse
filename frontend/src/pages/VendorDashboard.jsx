import React, { useState, useEffect } from "react";
import {
  UserPlus,
  FileText,
  RefreshCw,
  TrendingUp,
  Clock,
  LogOut,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import BidForm from "../components/BidForm";
import { vendorAPI } from "../services/api";

const VendorDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [view, setView] = useState("tenders"); // tenders, submit-bid, my-bids
  const [openTenders, setOpenTenders] = useState([]);
  const [myBids, setMyBids] = useState([]);
  const [selectedTender, setSelectedTender] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user && user.role === "vendor") {
      loadOpenTenders();
      loadMyBids(user.user_id);
    }
  }, [user]);

  const loadOpenTenders = async () => {
    try {
      const response = await vendorAPI.getOpenTenders();
      setOpenTenders(response.data);
    } catch (error) {
      console.error("Failed to load tenders:", error);
    }
  };

  const loadMyBids = async (vendorId) => {
    try {
      const response = await vendorAPI.getVendorBids(vendorId);
      setMyBids(response.data);
    } catch (error) {
      console.error("Failed to load bids:", error);
    }
  };

  const handleSubmitBid = async (bidData) => {
    try {
      await vendorAPI.submitBid(bidData);
      alert("✅ Bid submitted and logged on blockchain!");
      setView("my-bids");
      if (user) {
        loadMyBids(user.user_id);
      }
      loadOpenTenders();
    } catch (error) {
      if (error.response?.status === 400) {
        alert("❌ " + (error.response.data.detail || "Invalid bid submission"));
      } else {
        alert("❌ Failed to submit bid: " + error.message);
      }
    }
  };

  const handleLogout = () => {
    if (confirm("Are you sure you want to logout?")) {
      logout();
      navigate("/");
    }
  };

  // Submit Bid View
  if (view === "submit-bid" && selectedTender && user) {
    return (
      <div>
        <button
          onClick={() => setView("tenders")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Open Tenders
        </button>
        <BidForm
          tender={selectedTender}
          vendorId={user.user_id}
          onSubmit={handleSubmitBid}
          onCancel={() => setView("tenders")}
        />
      </div>
    );
  }

  // My Bids View
  if (view === "my-bids" && user) {
    return (
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">My Bids</h1>
          <div className="flex space-x-3">
            <button
              onClick={() => loadMyBids(user.user_id)}
              className="btn-secondary flex items-center"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
            <button onClick={() => setView("tenders")} className="btn-primary">
              Browse Tenders
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold mb-4">
            Bid History ({myBids.length})
          </h2>

          {myBids.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No bids submitted yet</p>
              <button
                onClick={() => setView("tenders")}
                className="btn-primary mt-4"
              >
                Browse Open Tenders
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {myBids.map((bid) => (
                <div
                  key={bid.bid_id}
                  className="border rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-bold text-lg">{bid.tender_title}</h3>
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Your Bid</p>
                          <p className="font-semibold text-primary-600">
                            ₹{bid.proposed_price.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">AI Score</p>
                          <p
                            className={`font-bold ${
                              bid.ai_score >= 75
                                ? "text-green-600"
                                : bid.ai_score >= 50
                                ? "text-yellow-600"
                                : "text-red-600"
                            }`}
                          >
                            {bid.ai_score ? bid.ai_score.toFixed(1) : "Pending"}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Status</p>
                          <span
                            className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                              bid.status === "accepted"
                                ? "bg-green-100 text-green-800"
                                : bid.status === "rejected"
                                ? "bg-red-100 text-red-800"
                                : bid.status === "under_review"
                                ? "bg-blue-100 text-blue-800"
                                : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {bid.status.replace("_", " ")}
                          </span>
                        </div>
                        <div>
                          <p className="text-gray-500">Submitted</p>
                          <p className="text-sm">
                            {new Date(bid.submitted_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default: Open Tenders View
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200 mb-6">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-600 to-green-700 rounded-xl flex items-center justify-center shadow-lg">
                <Users className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  Vendor Dashboard
                </h1>
                <p className="text-xs text-gray-500 font-medium">
                  Welcome, {user.name || user.vendor_id}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setView("my-bids")}
                className="btn-secondary flex items-center"
              >
                <FileText className="w-4 h-4 mr-2" />
                My Bids
              </button>
              <button
                onClick={loadOpenTenders}
                className="btn-secondary flex items-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 flex items-center transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <TrendingUp className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">{openTenders.length}</p>
          <p className="text-sm">Open Tenders</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <FileText className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">{myBids.length}</p>
          <p className="text-sm">Bids Submitted</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <Clock className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {myBids.filter((b) => b.status === "under_review").length}
          </p>
          <p className="text-sm">Under Review</p>
        </div>
      </div>

      {/* Open Tenders */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Available Tenders</h2>

        {openTenders.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">
              No open tenders available at the moment
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {openTenders.map((tender) => {
              const hasSubmitted = myBids.some(
                (bid) => bid.tender_title === tender.title
              );
              const deadline = new Date(tender.deadline);
              const timeLeft = Math.ceil(
                (deadline - new Date()) / (1000 * 60 * 60 * 24)
              );

              return (
                <div
                  key={tender.id}
                  className="border rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-bold text-lg">{tender.title}</h3>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {tender.description}
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                          {tender.category}
                        </span>
                        <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                          {tender.department}
                        </span>
                      </div>

                      <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Budget</p>
                          <p className="font-semibold text-primary-600">
                            ₹{tender.budget.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Deadline</p>
                          <p className="font-semibold">
                            {deadline.toLocaleDateString()}
                          </p>
                          <p
                            className={`text-xs ${
                              timeLeft <= 3 ? "text-red-600" : "text-gray-500"
                            }`}
                          >
                            {timeLeft} days left
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-500">Status</p>
                          <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                            {tender.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="ml-4">
                      {hasSubmitted ? (
                        <span className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium">
                          ✓ Bid Submitted
                        </span>
                      ) : user ? (
                        <button
                          onClick={() => {
                            setSelectedTender(tender);
                            setView("submit-bid");
                          }}
                          className="btn-primary"
                        >
                          Submit Bid
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default VendorDashboard;
