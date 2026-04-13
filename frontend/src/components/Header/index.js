import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className="header">
      <div className="header-left">
        <Link to="/" className="logo">
          📊 NewsAggregator
        </Link>
      </div>

      <div className="header-right">
        {isAuthenticated ? (
          <div className="user-menu">
            <Link to="/bookmarks">Закладки</Link>
            <Link to="/subscriptions">Подписки</Link>
            <span className="user-email">{user?.email}</span>
            <button onClick={logout} className="btn-logout">
              Выйти
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn-login">
            Войти
          </Link>
        )}
      </div>
    </header>
  );
}
