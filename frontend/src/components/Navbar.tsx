import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ThemeToggle } from './ui/theme-toggle';
import { Button } from './ui/button';
import { Menu, X, User, LogOut, Settings } from 'lucide-react';
import { NotificationCenter } from './ui/notification-center';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  const changeLanguage = (lng: string) => i18n.changeLanguage(lng);
  return (
    <select
      value={i18n.language}
      onChange={e => changeLanguage(e.target.value)}
      className="rounded border px-2 py-1 text-sm bg-background text-foreground"
      style={{ minWidth: 60 }}
      aria-label="Select language"
    >
      <option value="en">EN</option>
      <option value="es">ES</option>
    </select>
  );
};

const Navbar = () => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/dashboard', label: t('dashboard') },
    { path: '/custom-dashboard', label: t('custom_dashboard', 'Custom Dashboard') },
    { path: '/lead-collection', label: t('leads', 'Leads') },
    { path: '/crm', label: t('crm') },
    { path: '/analytics', label: t('analytics') },
    { path: '/teams', label: t('teams', 'Teams') },
  ];

  const adminItems = [
    { path: '/admin', label: t('admin', 'Admin') },
    { path: '/audit-log', label: t('audit_log', 'Audit Log') },
  ];

  useEffect(() => {
    setIsMenuOpen(false);
  }, [location]);

  const handleLogout = () => {
    logout();
    setIsDropdownOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className="flex items-center space-x-2" aria-label="Home">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">L</span>
              </div>
              <span className="text-xl font-bold text-foreground">LeadTap</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-label={item.label}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
              {user?.role === 'admin' && adminItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-label={item.label}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Right side items */}
          <div className="hidden md:flex items-center space-x-4">
            <NotificationCenter />
            <ThemeToggle />
            <LanguageSwitcher />
            {user ? (
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label="User menu"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center space-x-2"
                >
                  <User className="h-4 w-4" />
                  <span>{user.email}</span>
                </Button>
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-card border border-border rounded-md shadow-lg py-1 z-50">
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-foreground hover:bg-accent"
                      onClick={() => setIsDropdownOpen(false)}
                      aria-label="Profile settings"
                    >
                      <Settings className="h-4 w-4 mr-2" />
                      {t('settings', 'Settings')}
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-4 py-2 text-sm text-foreground hover:bg-accent"
                      aria-label="Logout"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      {t('logout')}
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link to="/login">
                  <Button variant="ghost" size="sm" aria-label="Login">
                    {t('login')}
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm" aria-label="Sign Up">
                    {t('sign_up', 'Sign Up')}
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-card border-t border-border">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                aria-label={item.label}
                className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                {item.label}
              </Link>
            ))}
            {user?.role === 'admin' && adminItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                aria-label={item.label}
                className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                {item.label}
              </Link>
            ))}
            {user ? (
              <div className="pt-4 border-t border-border">
                <Link
                  to="/profile"
                  className="block px-3 py-2 text-base font-medium text-muted-foreground hover:text-foreground hover:bg-accent"
                  aria-label="Profile settings"
                >
                  {t('settings', 'Settings')}
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 text-base font-medium text-muted-foreground hover:text-foreground hover:bg-accent"
                  aria-label="Logout"
                >
                  {t('logout')}
                </button>
              </div>
            ) : (
              <div className="pt-4 border-t border-border space-y-2">
                <Link to="/login">
                  <Button variant="ghost" className="w-full justify-start" aria-label="Login">
                    {t('login')}
                  </Button>
                </Link>
                <Link to="/register">
                  <Button className="w-full justify-start" aria-label="Sign Up">
                    {t('sign_up', 'Sign Up')}
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar; 