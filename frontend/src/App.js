import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import NewsDetail from "./components/NewsDetail";
import LoginForm from "./components/LoginForm";
import Bookmarks from "./components/Bookmarks";
import Subscriptions from "./components/Subscriptions";
import Privacy from "./components/Privacy";
import { useAuth } from "./hooks/useAuth";

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/login" element={<LoginForm />} />
      <Route path="/news/:id" element={<NewsDetail />} />
      <Route
        path="/bookmarks"
        element={
          <PrivateRoute>
            <Bookmarks />
          </PrivateRoute>
        }
      />
      <Route
        path="/subscriptions"
        element={
          <PrivateRoute>
            <Subscriptions />
          </PrivateRoute>
        }
      />
      <Route path="/privacy" element={<Privacy />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Header />
          <main className="main-content">
            <AppRoutes />
          </main>
        </div>
      </AuthProvider>
    </Router>
  );
}
