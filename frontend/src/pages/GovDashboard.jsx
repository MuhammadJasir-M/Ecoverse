import React, { useState, useEffect } from "react";
import { Plus, RefreshCw, Award, FileText, AlertCircle, LogOut, Building2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import TenderForm from "../components/TenderForm";
import AIRecommendationTable from "../components/AIRecommendationTable";
import { govAPI } from "../services/api";

const GovDashboard = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [view, setView] = useState("list"); // list, create, recommendations, award
  const [tenders, setTenders] = useState([]);
  const [selectedTender, setSelectedTender] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWinner, setSelectedWinner] = useState(null);
  const [awardForm, setAwardForm] = useState({
    justification: "",
    contract_start: "",
    contract_end: "",
  });

  const handleLogout = () => {
    if (confirm("Are you sure you want to logout?")) {
      logout();
      navigate("/");
    }
  };

  useEffect(() => {
    loadTenders();
  }, []);

  const loadTenders = async () => {
    try {
      const response = await govAPI.getTenders();
      setTenders(response.data);
    } catch (error) {
      console.error("Failed to load tenders:", error);
    }
  };

  const handleCreateTender = async (data) => {
    try {
      setLoading(true);
      await govAPI.createTender(data);
      alert("✅ Tender created and logged on blockchain!");
      setView("list");
      loadTenders();
    } catch (error) {
      alert("❌ Failed to create tender: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTender = async (tenderId) => {
    if (!confirm("Are you sure you want to close this tender for bidding?"))
      return;

    try {
      await govAPI.closeTender(tenderId);
      alert("✅ Tender closed successfully");
      loadTenders();
    } catch (error) {
      alert("❌ Failed to close tender");
    }
  };

  const handleViewBids = async (tender) => {
    try {
      setLoading(true);
      setSelectedTender(tender);
      const response = await govAPI.getTenderBids(tender.id);
      setBids(response.data);
      setView("bids");
    } catch (error) {
      alert("❌ Failed to load bids");
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendations = async (tender) => {
    try {
      setLoading(true);
      setSelectedTender(tender);
      const response = await govAPI.getRecommendations(tender.id);
      setRecommendations(response.data.recommendations);
      setView("recommendations");
    } catch (error) {
      alert("❌ Failed to get recommendations");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWinner = (bidId) => {
    setSelectedWinner(bidId);
    setView("award");
  };

  const handleSubmitAward = async (e) => {
    e.preventDefault();

    if (!awardForm.justification || awardForm.justification.length < 50) {
      alert("Please provide a detailed justification (minimum 50 characters)");
      return;
    }

    if (!awardForm.contract_start || !awardForm.contract_end) {
      alert("Please provide contract start and end dates");
      return;
    }

    try {
      setLoading(true);
      await govAPI.createAward({
        tender_id: selectedTender.id,
        winning_bid_id: selectedWinner,
        justification: awardForm.justification,
        contract_start: new Date(awardForm.contract_start).toISOString(),
        contract_end: new Date(awardForm.contract_end).toISOString(),
      });

      alert("✅ Award created and logged on blockchain!");
      setView("list");
      setSelectedWinner(null);
      setAwardForm({ justification: "", contract_start: "", contract_end: "" });
      loadTenders();
    } catch (error) {
      alert("❌ Failed to create award: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Render Views
  if (view === "create") {
    return (
      <div>
        <button
          onClick={() => setView("list")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Dashboard
        </button>
        <TenderForm
          onSubmit={handleCreateTender}
          onCancel={() => setView("list")}
        />
      </div>
    );
  }

  if (view === "bids" && selectedTender) {
    return (
      <div>
        <button
          onClick={() => setView("list")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Dashboard
        </button>
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">{selectedTender.title}</h2>
          <h3 className="text-lg font-semibold mb-4">
            Submitted Bids ({bids.length})
          </h3>

          {bids.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No bids submitted yet
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-3 text-left">Vendor</th>
                    <th className="px-4 py-3 text-right">Price</th>
                    <th className="px-4 py-3 text-center">Timeline</th>
                    <th className="px-4 py-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bids.map((bid) => (
                    <tr key={bid.id} className="border-b">
                      <td className="px-4 py-3">{bid.vendor_name}</td>
                      <td className="px-4 py-3 text-right">
                        ₹{bid.proposed_price.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {bid.delivery_timeline} days
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                          {bid.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <button
            onClick={() => handleGetRecommendations(selectedTender)}
            className="btn-primary mt-6"
          >
            Get AI Recommendations
          </button>
        </div>
      </div>
    );
  }

  if (view === "recommendations" && selectedTender) {
    return (
      <div>
        <button
          onClick={() => setView("list")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Dashboard
        </button>
        <AIRecommendationTable
          recommendations={recommendations}
          onSelectWinner={handleSelectWinner}
          selectedBidId={selectedWinner}
        />
      </div>
    );
  }

  if (view === "award" && selectedTender && selectedWinner) {
    return (
      <div>
        <button
          onClick={() => setView("recommendations")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Recommendations
        </button>
        <div className="card max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Award Tender</h2>
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <p className="font-semibold">{selectedTender.title}</p>
            <p className="text-sm text-gray-600">
              Selected Bid ID: {selectedWinner}
            </p>
          </div>

          <form onSubmit={handleSubmitAward} className="space-y-4">
            <div>
              <label className="label">Justification *</label>
              <textarea
                value={awardForm.justification}
                onChange={(e) =>
                  setAwardForm((prev) => ({
                    ...prev,
                    justification: e.target.value,
                  }))
                }
                rows="5"
                className="input"
                placeholder="Explain why this bid was selected based on AI recommendations, evaluation criteria, and decision factors..."
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                {awardForm.justification.length} / 50 minimum characters
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Contract Start Date *</label>
                <input
                  type="date"
                  value={awardForm.contract_start}
                  onChange={(e) =>
                    setAwardForm((prev) => ({
                      ...prev,
                      contract_start: e.target.value,
                    }))
                  }
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="label">Contract End Date *</label>
                <input
                  type="date"
                  value={awardForm.contract_end}
                  onChange={(e) =>
                    setAwardForm((prev) => ({
                      ...prev,
                      contract_end: e.target.value,
                    }))
                  }
                  className="input"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading
                ? "Creating Award..."
                : "Finalize Award & Log on Blockchain"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Default: Tender List
  return (
    <div>
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200 mb-6">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <Building2 className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  Government Dashboard
                </h1>
                <p className="text-xs text-gray-500 font-medium">
                  Tender Management & Award Decisions
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={loadTenders}
                className="btn-secondary flex items-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
              <button
                onClick={() => setView("create")}
                className="btn-primary flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Tender
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <FileText className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">{tenders.length}</p>
          <p className="text-sm">Total Tenders</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <FileText className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {tenders.filter((t) => t.status === "open").length}
          </p>
          <p className="text-sm">Open Tenders</p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <FileText className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {tenders.filter((t) => t.status === "closed").length}
          </p>
          <p className="text-sm">Closed Tenders</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <Award className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {tenders.filter((t) => t.status === "awarded").length}
          </p>
          <p className="text-sm">Awarded</p>
        </div>
      </div>

      {/* Tender List */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">All Tenders</h2>
        {tenders.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No tenders created yet
          </p>
        ) : (
          <div className="space-y-4">
            {tenders.map((tender) => (
              <div
                key={tender.id}
                className="border rounded-lg p-4 hover:bg-gray-50"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg">{tender.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {tender.category} • {tender.department}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Budget: ₹{tender.budget.toLocaleString()} | Deadline:{" "}
                      {new Date(tender.deadline).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        tender.status === "open"
                          ? "bg-green-100 text-green-800"
                          : tender.status === "closed"
                          ? "bg-yellow-100 text-yellow-800"
                          : tender.status === "awarded"
                          ? "bg-purple-100 text-purple-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {tender.status}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewBids(tender)}
                        className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        View Bids
                      </button>
                      {tender.status === "open" && (
                        <button
                          onClick={() => handleCloseTender(tender.id)}
                          className="text-sm px-3 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
                        >
                          Close
                        </button>
                      )}
                      {tender.status === "closed" && (
                        <button
                          onClick={() => handleGetRecommendations(tender)}
                          className="text-sm px-3 py-1 bg-primary-100 text-primary-700 rounded hover:bg-primary-200"
                        >
                          AI Recommend
                        </button>
                      )}
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
};

export default GovDashboard;
