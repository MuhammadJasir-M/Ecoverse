import React, { useState } from "react";
import { Star, MessageSquare, User } from "lucide-react";

const RatingForm = ({ awardId, tenderTitle, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    rating: 0,
    feedback: "",
    citizen_name: "",
  });

  const [hoveredStar, setHoveredStar] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.rating === 0) {
      setError("Please select a rating");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit({
        award_id: awardId,
        rating: formData.rating,
        feedback: formData.feedback || null,
        citizen_name: formData.citizen_name || null,
      });

      // Reset form
      setFormData({
        rating: 0,
        feedback: "",
        citizen_name: "",
      });
    } catch (err) {
      setError("Failed to submit rating. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleStarClick = (star) => {
    setFormData((prev) => ({ ...prev, rating: star }));
    setError("");
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        Rate This Project
      </h2>
      <p className="text-gray-600 mb-6">{tenderTitle}</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Star Rating */}
        <div>
          <label className="label">Your Rating *</label>
          <div className="flex items-center space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => handleStarClick(star)}
                onMouseEnter={() => setHoveredStar(star)}
                onMouseLeave={() => setHoveredStar(0)}
                className="focus:outline-none transition-transform hover:scale-110"
              >
                <Star
                  className={`w-10 h-10 ${
                    star <= (hoveredStar || formData.rating)
                      ? "fill-yellow-400 text-yellow-400"
                      : "text-gray-300"
                  }`}
                />
              </button>
            ))}
            {formData.rating > 0 && (
              <span className="ml-4 text-lg font-semibold text-gray-700">
                {formData.rating} / 5
              </span>
            )}
          </div>
          {formData.rating > 0 && (
            <p className="text-sm text-gray-600 mt-2">
              {formData.rating === 5 && "⭐ Excellent!"}
              {formData.rating === 4 && "👍 Very Good!"}
              {formData.rating === 3 && "😊 Good"}
              {formData.rating === 2 && "😐 Fair"}
              {formData.rating === 1 && "😞 Poor"}
            </p>
          )}
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </div>

        {/* Feedback */}
        <div>
          <label className="label">
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Feedback (Optional)
          </label>
          <textarea
            name="feedback"
            value={formData.feedback}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, feedback: e.target.value }))
            }
            rows="4"
            className="input"
            placeholder="Share your experience with this project's execution, quality, and overall satisfaction..."
          />
          <p className="text-xs text-gray-500 mt-1">
            Your feedback helps improve future projects and vendor
            accountability
          </p>
        </div>

        {/* Name (Optional) */}
        <div>
          <label className="label">
            <User className="w-4 h-4 inline mr-2" />
            Your Name (Optional)
          </label>
          <input
            type="text"
            name="citizen_name"
            value={formData.citizen_name}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, citizen_name: e.target.value }))
            }
            className="input"
            placeholder="Anonymous by default"
          />
        </div>

        {/* Actions */}
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading || formData.rating === 0}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Submitting..." : "Submit Rating"}
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

export default RatingForm;
