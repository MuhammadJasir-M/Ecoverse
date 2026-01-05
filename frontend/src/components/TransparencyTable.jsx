import React from "react";
import { ExternalLink, Shield, CheckCircle, XCircle } from "lucide-react";

const TransparencyTable = ({ data }) => {
  if (!data) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-500">Loading transparency data...</p>
      </div>
    );
  }

  const { tender, all_bids, award, blockchain_proof } = data;

  return (
    <div className="space-y-6">
      {/* Tender Information */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Tender Details</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">Tender ID</p>
            <p className="font-semibold">{tender.id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Title</p>
            <p className="font-semibold">{tender.title}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Budget</p>
            <p className="font-semibold">₹{tender.budget.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Department</p>
            <p className="font-semibold">{tender.department}</p>
          </div>
        </div>
      </div>

      {/* Blockchain Verification */}
      {blockchain_proof && (
        <div className="card bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800 flex items-center">
              <Shield className="w-6 h-6 mr-2 text-blue-600" />
              Blockchain Verification
            </h3>
            {blockchain_proof.tender_verified &&
            blockchain_proof.award_verified ? (
              <span className="flex items-center text-green-600 font-semibold">
                <CheckCircle className="w-5 h-5 mr-1" />
                Verified
              </span>
            ) : (
              <span className="flex items-center text-red-600 font-semibold">
                <XCircle className="w-5 h-5 mr-1" />
                Incomplete
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Tender Creation</p>
              <p
                className={`font-semibold ${
                  blockchain_proof.tender_verified
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {blockchain_proof.tender_verified
                  ? "✓ Verified"
                  : "✗ Not Verified"}
              </p>
              {blockchain_proof.tender_timestamp > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(
                    blockchain_proof.tender_timestamp * 1000
                  ).toLocaleString()}
                </p>
              )}
            </div>

            <div className="p-4 bg-white rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Total Bids</p>
              <p className="font-semibold text-primary-600 text-2xl">
                {blockchain_proof.total_bids}
              </p>
            </div>

            <div className="p-4 bg-white rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Award Decision</p>
              <p
                className={`font-semibold ${
                  blockchain_proof.award_verified
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {blockchain_proof.award_verified
                  ? "✓ Verified"
                  : "✗ Not Verified"}
              </p>
              {blockchain_proof.award_timestamp > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(
                    blockchain_proof.award_timestamp * 1000
                  ).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* All Bids Comparison */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          All Submitted Bids ({all_bids?.length || 0})
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b-2 border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                  Vendor
                </th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
                  Proposed Price
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                  Timeline
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                  AI Score
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                  Status
                </th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">
                  Anomaly
                </th>
              </tr>
            </thead>
            <tbody>
              {all_bids &&
                all_bids.map((bid, index) => (
                  <tr
                    key={index}
                    className={`border-b hover:bg-gray-50 ${
                      bid.status === "accepted" ? "bg-green-50" : ""
                    }`}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center">
                        {bid.status === "accepted" && (
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        )}
                        <span className="font-medium">{bid.vendor_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-semibold">
                      ₹{bid.proposed_price.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {bid.delivery_timeline} days
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`font-bold ${
                          bid.ai_score >= 75
                            ? "text-green-600"
                            : bid.ai_score >= 50
                            ? "text-yellow-600"
                            : "text-red-600"
                        }`}
                      >
                        {bid.ai_score ? bid.ai_score.toFixed(1) : "N/A"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          bid.status === "accepted"
                            ? "bg-green-100 text-green-800"
                            : bid.status === "rejected"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {bid.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {bid.anomaly_flag ? (
                        <span className="text-red-600 text-xs font-medium">
                          ⚠ Flagged
                        </span>
                      ) : (
                        <span className="text-green-600">✓</span>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Award Information */}
      {award && (
        <div className="card bg-gradient-to-r from-green-50 to-emerald-50">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Award Decision
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Winning Amount</p>
              <p className="text-2xl font-bold text-green-600">
                ₹{award.winning_amount?.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Justification</p>
              <p className="text-gray-800">{award.justification}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransparencyTable;
