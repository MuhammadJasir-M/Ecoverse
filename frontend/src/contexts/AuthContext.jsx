import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../services/api";

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    const token = localStorage.getItem("auth_token");
    const userData = localStorage.getItem("user_data");
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        // Verify token is still valid by checking user info
        authAPI.getCurrentUser()
          .then((response) => {
            setUser(response.data);
            localStorage.setItem("user_data", JSON.stringify(response.data));
          })
          .catch(() => {
            // Token invalid, clear storage
            logout();
          })
          .finally(() => setLoading(false));
      } catch (error) {
        logout();
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (role, credentials) => {
    try {
      let response;
      
      if (role === "government") {
        response = await authAPI.governmentLogin(credentials.access_code);
      } else if (role === "vendor") {
        response = await authAPI.vendorLogin(credentials.vendor_id, credentials.password);
      } else {
        throw new Error("Invalid role");
      }

      const { access_token, role: userRole, user_id, vendor_id, name } = response.data;
      
      const userData = {
        role: userRole,
        user_id,
        vendor_id,
        name,
        token: access_token,
      };

      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("user_data", JSON.stringify(userData));
      setUser(userData);
      
      return userData;
    } catch (error) {
      throw error;
    }
  };

  const register = async (vendorData) => {
    try {
      const response = await authAPI.vendorRegister(vendorData);
      
      const { access_token, role: userRole, user_id, vendor_id, name } = response.data;
      
      const userData = {
        role: userRole,
        user_id,
        vendor_id,
        name,
        token: access_token,
      };

      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("user_data", JSON.stringify(userData));
      setUser(userData);
      
      return userData;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_data");
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
    isGovernment: user?.role === "government",
    isVendor: user?.role === "vendor",
    isPublic: user?.role === "public" || !user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

