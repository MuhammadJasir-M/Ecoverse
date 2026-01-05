import React, { useState } from "react";
import { Calendar, DollarSign, FileText, Building } from "lucide-react";

const TenderForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    budget: "",
    department: "",
    deadline: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const categories = [
    "Infrastructure",
    "IT & Software",
    "Construction",
    "Healthcare",
    "Education",
    "Transportation",
    "Consulting",
    "Equipment",
    "Maintenance",
    "Others",
  ];

  const validate = () => {
    const newErrors = {};

    if (!formData.title || formData.title.length < 10) {
      newErrors.title = "Title must be at least 10 characters";
    }

    if (!formData.description || formData.description.length < 50) {
      newErrors.description = "Description must be at least 50 characters";
    }

    if (!formData.category) {
      newErrors.category = "Please select a category";
    }

    if (!formData.budget || parseFloat(formData.budget) <= 0) {
      newErrors.budget = "Budget must be greater than 0";
    }

    if (!formData.department) {
      newErrors.department = "Department is required";
    }

    if (!formData.deadline) {
      newErrors.deadline = "Deadline is required";
    } else {
      const deadlineDate = new Date(formData.deadline);
      const today = new Date();
      if (deadlineDate <= today) {
        newErrors.deadline = "Deadline must be in the future";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      const submitData = {
        ...formData,
        budget: parseFloat(formData.budget),
        deadline: new Date(formData.deadline).toISOString(),
      };

      await onSubmit(submitData);

      // Reset form
      setFormData({
        title: "",
        description: "",
        category: "",
        budget: "",
        department: "",
        deadline: "",
      });
    } catch (error) {
      console.error("Tender creation failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  return (
    <div className="card max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Create New Tender
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="label">
            <FileText className="w-4 h-4 inline mr-2" />
            Tender Title *
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className={`input ${errors.title ? "border-red-500" : ""}`}
            placeholder="e.g., Smart City Infrastructure Development"
          />
          {errors.title && (
            <p className="text-red-500 text-sm mt-1">{errors.title}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="label">Description *</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="5"
            className={`input ${errors.description ? "border-red-500" : ""}`}
            placeholder="Provide detailed description of the tender requirements, scope of work, deliverables, and evaluation criteria..."
          />
          <p className="text-sm text-gray-500 mt-1">
            {formData.description.length} characters (minimum 50)
          </p>
          {errors.description && (
            <p className="text-red-500 text-sm mt-1">{errors.description}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Category */}
          <div>
            <label className="label">Category *</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className={`input ${errors.category ? "border-red-500" : ""}`}
            >
              <option value="">Select Category</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="text-red-500 text-sm mt-1">{errors.category}</p>
            )}
          </div>

          {/* Budget */}
          <div>
            <label className="label">
              <DollarSign className="w-4 h-4 inline mr-2" />
              Budget (₹) *
            </label>
            <input
              type="number"
              name="budget"
              value={formData.budget}
              onChange={handleChange}
              step="0.01"
              min="0"
              className={`input ${errors.budget ? "border-red-500" : ""}`}
              placeholder="e.g., 5000000"
            />
            {errors.budget && (
              <p className="text-red-500 text-sm mt-1">{errors.budget}</p>
            )}
          </div>

          {/* Department */}
          <div>
            <label className="label">
              <Building className="w-4 h-4 inline mr-2" />
              Department *
            </label>
            <input
              type="text"
              name="department"
              value={formData.department}
              onChange={handleChange}
              className={`input ${errors.department ? "border-red-500" : ""}`}
              placeholder="e.g., Public Works Department"
            />
            {errors.department && (
              <p className="text-red-500 text-sm mt-1">{errors.department}</p>
            )}
          </div>

          {/* Deadline */}
          <div>
            <label className="label">
              <Calendar className="w-4 h-4 inline mr-2" />
              Bid Deadline *
            </label>
            <input
              type="datetime-local"
              name="deadline"
              value={formData.deadline}
              onChange={handleChange}
              className={`input ${errors.deadline ? "border-red-500" : ""}`}
            />
            {errors.deadline && (
              <p className="text-red-500 text-sm mt-1">{errors.deadline}</p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-4 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading
              ? "Creating Tender..."
              : "Create Tender & Log on Blockchain"}
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

export default TenderForm;
