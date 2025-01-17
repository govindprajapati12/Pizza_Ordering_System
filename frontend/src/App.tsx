import React, { useState, useEffect } from 'react';
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { Pizza, ShoppingCart, CreditCard, Settings } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import PizzaList from './components/PizzaList';
import Cart from './components/Cart';
import Orders from './components/orders';
import OrderDetail from './components/OrderDetail';
import AdminDashboard from './components/AdminDashboard';
import AuthModal from './components/AuthModal';
import LanguageSelector from './components/LanguageSelector';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [lastAttemptedPath, setLastAttemptedPath] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userRole = localStorage.getItem('user_role');
    if (token) {
      setAccessToken(token);
      setIsLoggedIn(true);
      setIsAdmin(userRole === 'admin');
    }
  }, []);

  const handleLogin = (token: string, role: string) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_role', role);
    setAccessToken(token);
    setIsLoggedIn(true);
    setIsAdmin(role === 'admin');
    setIsAuthModalOpen(false);
    
    if (lastAttemptedPath) {
      navigate(lastAttemptedPath);
      setLastAttemptedPath(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    setAccessToken(null);
    setIsLoggedIn(false);
    setIsAdmin(false);
    navigate('/');
  };

  const handleRegister = () => {
    console.log('Registration successful!');
  };

  const renderNavLink = (to: string, icon: React.ReactNode, label: string) => {
    const isActive = location.pathname === to || 
                    (to === '/orders' && location.pathname.startsWith('/orders/'));
    const handleClick = (e: React.MouseEvent) => {
      e.preventDefault();
      if (!isLoggedIn && ['/cart', '/orders', '/admin'].includes(to)) {
        setLastAttemptedPath(to);
        setIsAuthModalOpen(true);
      } else {
        navigate(to);
      }
    };

    return (
      <a
        href={to}
        onClick={handleClick}
        className={`flex items-center space-x-1 text-white hover:text-red-100 ${
          isActive ? 'border-b-2' : ''
        }`}
      >
        {icon}
        <span>{label}</span>
      </a>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-red-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Pizza size={32} />
              <h1 className="text-2xl font-bold">Pizza Paradise</h1>
            </div>
            <div className="flex items-center space-x-6">
              <nav className="flex space-x-4">
                {renderNavLink('/', <Pizza size={20} />, t('common.menu'))}
                {renderNavLink('/cart', <ShoppingCart size={20} />, t('common.cart'))}
                {isLoggedIn && renderNavLink('/orders', <CreditCard size={20} />, t('common.orders'))}
                {isAdmin && renderNavLink('/admin', <Settings size={20} />, t('common.admin'))}
              </nav>
              <div className="flex items-center space-x-4">
                <LanguageSelector />
                {!isLoggedIn ? (
                  <button
                    onClick={() => setIsAuthModalOpen(true)}
                    className="bg-white text-red-600 px-4 py-2 rounded-lg hover:bg-red-50"
                  >
                    {t('common.login')}
                  </button>
                ) : (
                  <button
                    onClick={handleLogout}
                    className="bg-red-700 text-white px-4 py-2 rounded-lg hover:bg-red-800"
                  >
                    {t('common.logout')}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<PizzaList />} />
          <Route
            path="/cart"
            element={isLoggedIn ? <Cart accessToken={accessToken} /> : <PizzaList />}
          />
          <Route
            path="/orders"
            element={isLoggedIn ? <Orders /> : <PizzaList />}
          />
          <Route
            path="/orders/:orderId"
            element={isLoggedIn ? <OrderDetail /> : <PizzaList />}
          />
          <Route
            path="/admin"
            element={isLoggedIn && isAdmin ? <AdminDashboard /> : <PizzaList />}
          />
        </Routes>
      </main>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
    </div>
  );
}

export default App;