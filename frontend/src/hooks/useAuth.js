import { useAuthContext } from "../context/AuthContext";

export function useAuth() {
  const { user, login, logout, loading } = useAuthContext();
  return { user, login, logout, loading, isAuthenticated: !!user };
}
