import React from "react";
import { TrendingUp, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

const AIRecommendationTable = ({
  recommendations,
  onSelectWinner,
  selectedBidId,
}) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500">No recommendations available yet.</p>
      </div>
    );
  }

  const getRecommendationBadge = (recommendation) => {
    switch (recommendation) {
      case "High":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-4 h-4 mr-1" />
            High
          </span>
        );
      case "Medium":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
            <TrendingUp className="w-4 h-4 mr-1" />
            Medium
          </span>
        );
      case "Low":
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <XCircle className="w-4 h-4 mr-1" />
            Low
          </span>
        );
      default:
        return null;
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return "text-green-600 font-bold";
    if (score >= 50) return "text-yellow-600 font-semibold";
    return "text-red-600";
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          AI-Powered Bid Recommendations
        </h2>
        <p className="text-sm text-gray-600">
          Bids analyzed using price optimization, vendor reputation, technical
          quality, and anomaly detection
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b-2 border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Rank
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Vendor
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
                Price
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                AI Score
                <span className="block text-xs font-normal text-gray-500">
                  Overall
                </span>
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Price
                <span className="block text-xs font-normal text-gray-500">
                  Score
                </span>
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Vendor
                <span className="block text-xs font-normal text-gray-500">
                  Score
                </span>
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Technical
                <span className="block text-xs font-normal text-gray-500">
                  Score
                </span>
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Timeline
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Status
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec, index) => (
              <tr
                key={rec.bid_id}
                className={`border-b hover:bg-gray-50 transition-colors ${
                  selectedBidId === rec.bid_id ? "bg-green-50" : ""
                } ${rec.anomaly_flag ? "bg-red-50" : ""}`}
              >
                {/* Rank */}
                <td className="px-4 py-4">
                  <div className="flex items-center">
                    <span
                      className={`text-2xl font-bold ${
                        index === 0 ? "text-yellow-500" : "text-gray-400"
                      }`}
                    >
                      #{index + 1}
                    </span>
                  </div>
                </td>

                {/* Vendor */}
                <td className="px-4 py-4">
                  <div>
                    <p className="font-medium text-gray-800">
                      {rec.vendor_name}
                    </p>
                    <p className="text-xs text-gray-500">ID: {rec.vendor_id}</p>
                  </div>
                </td>

                {/* Price */}
                <td className="px-4 py-4 text-right">
                  <p className="font-semibold text-gray-800">
                    ₹{rec.proposed_price.toLocaleString()}
                  </p>
                </td>

                {/* AI Score */}
                <td className="px-4 py-4 text-center">
                  <div className="flex flex-col items-center">
                    <span
                      className={`text-2xl font-bold ${getScoreColor(
                        rec.ai_score
                      )}`}
                    >
                      {rec.ai_score}
                    </span>
                    {getRecommendationBadge(rec.recommendation)}
                  </div>
                </td>

                {/* Price Score */}
                <td className="px-4 py-4 text-center">
                  <span className={getScoreColor(rec.price_score)}>
                    {rec.price_score}
                  </span>
                </td>

                {/* Vendor Score */}
                <td className="px-4 py-4 text-center">
                  <span className={getScoreColor(rec.vendor_score)}>
                    {rec.vendor_score}
                  </span>
                </td>

                {/* Technical Score */}
                <td className="px-4 py-4 text-center">
                  <span className={getScoreColor(rec.technical_score)}>
                    {rec.technical_score}
                  </span>
                </td>

                {/* Timeline */}
                <td className="px-4 py-4 text-center">
                  <span className="text-sm text-gray-600">
                    {rec.delivery_timeline} days
                  </span>
                </td>

                {/* Anomaly Status */}
                <td className="px-4 py-4 text-center">
                  {rec.anomaly_flag ? (
                    <div className="flex flex-col items-center">
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                      <span className="text-xs text-red-600 mt-1">Flagged</span>
                      {rec.anomaly_reason && (
                        <p className="text-xs text-gray-600 mt-1 max-w-xs">
                          {rec.anomaly_reason}
                        </p>
                      )}
                    </div>
                  ) : (
                    <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                  )}
                </td>

                {/* Action */}
                <td className="px-4 py-4 text-center">
                  <button
                    onClick={() => onSelectWinner(rec.bid_id)}
                    disabled={selectedBidId === rec.bid_id}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedBidId === rec.bid_id
                        ? "bg-green-600 text-white cursor-default"
                        : "bg-primary-600 text-white hover:bg-primary-700"
                    }`}
                  >
                    {selectedBidId === rec.bid_id
                      ? "Selected"
                      : "Select Winner"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-sm text-gray-700 mb-2">
          Scoring Breakdown:
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-600">
          <div>
            <span className="font-medium">Price Score:</span> Lower bid = Higher
            score
          </div>
          <div>
            <span className="font-medium">Vendor Score:</span> Reputation + Past
            work
          </div>
          <div>
            <span className="font-medium">Technical Score:</span> Proposal
            quality + Timeline
          </div>
          <div>
            <span className="font-medium">Anomaly Detection:</span> Fraud
            pattern analysis
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIRecommendationTable;
