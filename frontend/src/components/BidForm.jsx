import React, { useState } from "react";
import { DollarSign, FileText, Clock, User } from "lucide-react";

const BidForm = ({ tender, vendorId, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    proposed_price: "",
    technical_proposal: "",
    delivery_timeline: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const newErrors = {};

    if (!formData.proposed_price || parseFloat(formData.proposed_price) <= 0) {
      newErrors.proposed_price = "Price must be greater than 0";
    }

    if (parseFloat(formData.proposed_price) > tender.budget * 1.2) {
      newErrors.proposed_price = "Price exceeds 120% of tender budget";
    }

    if (
      !formData.technical_proposal ||
      formData.technical_proposal.length < 100
    ) {
      newErrors.technical_proposal =
        "Technical proposal must be at least 100 characters";
    }

    if (
      !formData.delivery_timeline ||
      parseInt(formData.delivery_timeline) <= 0
    ) {
      newErrors.delivery_timeline =
        "Delivery timeline must be greater than 0 days";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);

    try {
      const submitData = {
        tender_id: tender.id,
        vendor_id: vendorId,
        proposed_price: parseFloat(formData.proposed_price),
        technical_proposal: formData.technical_proposal,
        delivery_timeline: parseInt(formData.delivery_timeline),
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error("Bid submission failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const pricePercentage = formData.proposed_price
    ? ((parseFloat(formData.proposed_price) / tender.budget) * 100).toFixed(1)
    : 0;

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Submit Bid</h2>
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-gray-700">{tender.title}</h3>
          <p className="text-sm text-gray-600 mt-1">
            Budget: ₹{tender.budget.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">
            Deadline: {new Date(tender.deadline).toLocaleString()}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Proposed Price */}
        <div>
          <label className="label">
            <DollarSign className="w-4 h-4 inline mr-2" />
            Proposed Price (₹) *
          </label>
          <input
            type="number"
            name="proposed_price"
            value={formData.proposed_price}
            onChange={handleChange}
            step="0.01"
            min="0"
            className={`input ${errors.proposed_price ? "border-red-500" : ""}`}
            placeholder={`Maximum: ₹${(tender.budget * 1.2).toLocaleString()}`}
          />
          {formData.proposed_price && (
            <p
              className={`text-sm mt-1 ${
                pricePercentage > 100 ? "text-orange-600" : "text-green-600"
              }`}
            >
              {pricePercentage}% of tender budget
            </p>
          )}
          {errors.proposed_price && (
            <p className="text-red-500 text-sm mt-1">{errors.proposed_price}</p>
          )}
        </div>

        {/* Delivery Timeline */}
        <div>
          <label className="label">
            <Clock className="w-4 h-4 inline mr-2" />
            Delivery Timeline (Days) *
          </label>
          <input
            type="number"
            name="delivery_timeline"
            value={formData.delivery_timeline}
            onChange={handleChange}
            min="1"
            className={`input ${
              errors.delivery_timeline ? "border-red-500" : ""
            }`}
            placeholder="e.g., 90"
          />
          {formData.delivery_timeline && (
            <p className="text-sm text-gray-500 mt-1">
              Approximately {Math.ceil(formData.delivery_timeline / 30)} months
            </p>
          )}
          {errors.delivery_timeline && (
            <p className="text-red-500 text-sm mt-1">
              {errors.delivery_timeline}
            </p>
          )}
        </div>

        {/* Technical Proposal */}
        <div>
          <label className="label">
            <FileText className="w-4 h-4 inline mr-2" />
            Technical Proposal *
          </label>
          <textarea
            name="technical_proposal"
            value={formData.technical_proposal}
            onChange={handleChange}
            rows="8"
            className={`input ${
              errors.technical_proposal ? "border-red-500" : ""
            }`}
            placeholder="Describe your approach, methodology, team qualifications, past experience, and why you're the best fit for this tender..."
          />
          <p className="text-sm text-gray-500 mt-1">
            {formData.technical_proposal.length} characters (minimum 100)
          </p>
          {errors.technical_proposal && (
            <p className="text-red-500 text-sm mt-1">
              {errors.technical_proposal}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 disabled:opacity-50"
          >
            {loading ? "Submitting Bid..." : "Submit Bid (Blockchain Recorded)"}
          </button>
          {onCancel && (
            <button type="button" onClick={onCancel} className="btn-secondary">
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default BidForm;
