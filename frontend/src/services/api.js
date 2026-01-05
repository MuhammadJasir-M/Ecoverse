import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log(
      `🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`
    );
    return config;
  },
  (error) => {
    console.error("❌ API Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized - clear auth and redirect
      if (error.response.status === 401) {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user_data");
        // Redirect to role selection if not already there
        if (window.location.pathname !== "/" && !window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
          window.location.href = "/";
        }
      }
      
      console.error(
        "❌ API Error Response:",
        error.response.status,
        error.response.data
      );
    } else if (error.request) {
      console.error("❌ API No Response:", error.request);
    } else {
      console.error("❌ API Error:", error.message);
    }
    return Promise.reject(error);
  }
);

// ==================== GOVERNMENT APIs ====================
export const govAPI = {
  // Create a new tender
  createTender: (data) => api.post("/gov/tenders", data),

  // Get all tenders
  getTenders: () => api.get("/gov/tenders"),

  // Get specific tender
  getTender: (tenderId) => api.get(`/gov/tenders/${tenderId}`),

  // Get bids for a tender
  getTenderBids: (tenderId) => api.get(`/gov/tenders/${tenderId}/bids`),

  // Close tender for bidding
  closeTender: (tenderId) => api.post(`/gov/tenders/${tenderId}/close`),

  // Get AI-powered recommendations
  getRecommendations: (tenderId) =>
    api.get(`/gov/tenders/${tenderId}/recommendations`),

  // Award tender to winning bid
  createAward: (data) => api.post("/gov/awards", data),

  // Get all awards
  getAwards: () => api.get("/gov/awards"),
};

// ==================== VENDOR APIs ====================
export const vendorAPI = {
  // Register new vendor
  register: (data) => {
    const params = new URLSearchParams();
    params.append("name", data.name);
    params.append("email", data.email);
    params.append("company_registration", data.company_registration);
    if (data.phone) params.append("phone", data.phone);
    if (data.address) params.append("address", data.address);

    return api.post("/vendor/register", params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  // Get all open tenders
  getOpenTenders: () => api.get("/vendor/tenders/open"),

  // Submit a bid
  submitBid: (data) => api.post("/vendor/bids", data),

  // Get vendor's bids
  getVendorBids: (vendorId) => api.get(`/vendor/bids/${vendorId}`),

  // Get vendor profile
  getVendorProfile: (vendorId) => api.get(`/vendor/profile/${vendorId}`),
};

// ==================== PUBLIC APIs ====================
export const publicAPI = {
  // Get all awarded tenders
  getAwardedTenders: () => api.get("/public/tenders/awarded"),

  // Get transparency view for a tender
  getTenderTransparency: (tenderId) =>
    api.get(`/public/tenders/${tenderId}/transparency`),

  // Submit public rating
  submitRating: (data) => api.post("/public/ratings", data),

  // Get ratings for an award
  getAwardRatings: (awardId) => api.get(`/public/ratings/${awardId}`),
};

// ==================== BLOCKCHAIN APIs ====================
export const blockchainAPI = {
  // Verify audit trail
  verifyAuditTrail: (tenderId) => api.get(`/blockchain/verify/${tenderId}`),

  // Get transaction details
  getTransaction: (txHash) => api.get(`/blockchain/transaction/${txHash}`),
};

// ==================== AUTHENTICATION APIs ====================
export const authAPI = {
  // Government login
  governmentLogin: (accessCode) => api.post("/auth/government/login", { access_code: accessCode }),
  
  // Vendor login
  vendorLogin: (vendorId, password) => api.post("/auth/vendor/login", { vendor_id: vendorId, password }),
  
  // Vendor register
  vendorRegister: (data) => api.post("/auth/vendor/register", data),
  
  // Get current user
  getCurrentUser: () => api.get("/auth/me"),
  
  // Logout
  logout: () => api.post("/auth/logout"),
};

// ==================== HEALTH CHECK ====================
export const healthCheck = () => api.get("/health");

// Export default instance
export default api;
