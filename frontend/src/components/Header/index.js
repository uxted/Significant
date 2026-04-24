import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold text-lg">Significant</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-2">
            {isAuthenticated ? (
              <>
                <Link
                  to="/bookmarks"
                  className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
                >
                  Закладки
                </Link>
                <Link
                  to="/subscriptions"
                  className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
                >
                  Подписки
                </Link>
                <span className="text-sm text-muted-foreground">{user?.email}</span>
                <button
                  onClick={logout}
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
                    bg-destructive text-destructive-foreground hover:bg-destructive/90
                    h-9 px-4 py-2"
                >
                  Выйти
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors
                  bg-primary text-primary-foreground hover:bg-primary/90
                  h-9 px-4 py-2"
              >
                Войти
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
