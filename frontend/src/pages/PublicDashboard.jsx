import React, { useState, useEffect } from "react";
import { Eye, Search, RefreshCw, Star, Shield, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import TransparencyTable from "../components/TransparencyTable";
import RatingForm from "../components/RatingForm";
import { publicAPI } from "../services/api";

const PublicDashboard = () => {
  const navigate = useNavigate();
  const [view, setView] = useState("list"); // list, transparency, rate
  const [awardedTenders, setAwardedTenders] = useState([]);
  const [selectedTender, setSelectedTender] = useState(null);
  const [transparencyData, setTransparencyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");

  useEffect(() => {
    loadAwardedTenders();
  }, []);

  const loadAwardedTenders = async () => {
    try {
      setLoading(true);
      const response = await publicAPI.getAwardedTenders();
      setAwardedTenders(response.data);
    } catch (error) {
      console.error("Failed to load awarded tenders:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTransparency = async (tender) => {
    try {
      setLoading(true);
      setSelectedTender(tender);
      const response = await publicAPI.getTenderTransparency(tender.tender_id);
      setTransparencyData(response.data);
      setView("transparency");
    } catch (error) {
      alert("❌ Failed to load transparency data");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitRating = async (ratingData) => {
    try {
      await publicAPI.submitRating(ratingData);
      alert("✅ Thank you for your feedback!");
      setView("list");
      loadAwardedTenders();
    } catch (error) {
      alert("❌ Failed to submit rating");
    }
  };

  const categories = ["all", ...new Set(awardedTenders.map((t) => t.category))];

  const filteredTenders = awardedTenders.filter((tender) => {
    const matchesSearch =
      tender.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tender.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      filterCategory === "all" || tender.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  // Transparency View
  if (view === "transparency" && selectedTender) {
    return (
      <div>
        <button
          onClick={() => setView("list")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Awarded Tenders
        </button>

        {loading ? (
          <div className="card text-center py-12">
            <RefreshCw className="w-12 h-12 mx-auto animate-spin text-primary-600 mb-4" />
            <p className="text-gray-600">Loading transparency data...</p>
          </div>
        ) : (
          <>
            <TransparencyTable data={transparencyData} />

            <div className="mt-6 text-center">
              <button
                onClick={() => setView("rate")}
                className="btn-primary inline-flex items-center"
              >
                <Star className="w-4 h-4 mr-2" />
                Rate This Project
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  // Rating View
  if (view === "rate" && selectedTender) {
    return (
      <div>
        <button
          onClick={() => setView("transparency")}
          className="mb-4 text-primary-600 hover:text-primary-700 font-medium"
        >
          ← Back to Transparency View
        </button>

        <RatingForm
          awardId={selectedTender.tender_id} // Using tender_id as award lookup
          tenderTitle={selectedTender.title}
          onSubmit={handleSubmitRating}
          onCancel={() => setView("transparency")}
        />
      </div>
    );
  }

  // Default: Awarded Tenders List
  return (
    <div>
      {/* Header with Back Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Public Transparency Portal
          </h1>
          <p className="text-gray-600">
            View awarded government tenders, verify blockchain records, and
            provide citizen feedback
          </p>
        </div>
        <button
          onClick={() => navigate("/")}
          className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Role Selection
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <Eye className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">{awardedTenders.length}</p>
          <p className="text-sm">Awarded Tenders</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <Shield className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {awardedTenders.filter((t) => t.creation_tx && t.award_tx).length}
          </p>
          <p className="text-sm">Blockchain Verified</p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <Star className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {awardedTenders.filter((t) => t.public_rating).length}
          </p>
          <p className="text-sm">Projects Rated</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <Star className="w-8 h-8 mb-2" />
          <p className="text-3xl font-bold">
            {awardedTenders.reduce(
              (sum, t) => sum + (t.public_rating || 0),
              0
            ) / (awardedTenders.filter((t) => t.public_rating).length || 1)}
          </p>
          <p className="text-sm">Avg Rating</p>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title or department..."
                className="input pl-10"
              />
            </div>
          </div>
          <div className="md:w-64">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="input"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "all" ? "All Categories" : cat}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={loadAwardedTenders}
            className="btn-secondary flex items-center justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Awarded Tenders List */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">
          Awarded Tenders ({filteredTenders.length})
        </h2>

        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 mx-auto animate-spin text-primary-600 mb-4" />
            <p className="text-gray-600">Loading...</p>
          </div>
        ) : filteredTenders.length === 0 ? (
          <div className="text-center py-12">
            <Eye className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No awarded tenders found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredTenders.map((tender) => (
              <div
                key={tender.tender_id}
                className="border rounded-lg p-5 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-bold text-lg text-gray-800">
                        {tender.title}
                      </h3>
                      {tender.creation_tx && tender.award_tx && (
                        <span className="flex items-center text-green-600 text-sm font-medium ml-4">
                          <Shield className="w-4 h-4 mr-1" />
                          Blockchain Verified
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-2 mb-3">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        {tender.category}
                      </span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                        {tender.department}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Original Budget</p>
                        <p className="font-semibold">
                          ₹{tender.budget.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Award Amount</p>
                        <p className="font-semibold text-green-600">
                          ₹{tender.award_amount.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Winner</p>
                        <p className="font-semibold text-primary-600">
                          {tender.winner}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Public Rating</p>
                        <div className="flex items-center">
                          {tender.public_rating ? (
                            <>
                              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400 mr-1" />
                              <span className="font-semibold">
                                {tender.public_rating.toFixed(1)}
                              </span>
                              <span className="text-xs text-gray-500 ml-1">
                                ({tender.feedback_count})
                              </span>
                            </>
                          ) : (
                            <span className="text-gray-400 text-sm">
                              Not rated yet
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="mt-3 text-sm text-gray-600">
                      <p>
                        <strong>Contract Period:</strong>{" "}
                        {new Date(tender.contract_start).toLocaleDateString()} -{" "}
                        {new Date(tender.contract_end).toLocaleDateString()}
                      </p>
                      <p className="mt-1 line-clamp-2">
                        <strong>Justification:</strong> {tender.justification}
                      </p>
                    </div>
                  </div>

                  <div className="ml-4 flex flex-col space-y-2">
                    <button
                      onClick={() => handleViewTransparency(tender)}
                      className="btn-primary whitespace-nowrap flex items-center"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 card bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-primary-600">
        <div className="flex items-start">
          <Shield className="w-6 h-6 text-primary-600 mr-3 mt-1 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-gray-800 mb-1">
              Why Blockchain Verification Matters
            </h4>
            <p className="text-sm text-gray-600">
              Every tender creation, bid submission, and award decision is
              permanently recorded on the blockchain. This ensures complete
              transparency, prevents tampering, and allows citizens to verify
              the integrity of government procurement processes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicDashboard;
