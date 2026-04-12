import React, { createContext, useState, useContext, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (token in memory)
    const storedUser = sessionStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await api.post("/api/auth/login/", { email, password });
    const { access, refresh } = response.data;
    api.setTokens(access, refresh);

    // Fetch user profile
    const profile = await api.get("/api/user/profile/");
    setUser(profile.data);
    sessionStorage.setItem("user", JSON.stringify(profile.data));
    return profile.data;
  };

  const logout = () => {
    api.clearTokens();
    setUser(null);
    sessionStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  return useContext(AuthContext);
}
