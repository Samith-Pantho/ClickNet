import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation} from 'react-router-dom';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import ChatBot from '../../components/banking/ChatBot';
import { useAuth } from '../../contexts/AuthContext';
import Modal from '../../components/common/Modal';
import backgroundImage from '../../assets/images/Bg.png'; 

const MasterPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('home');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Sync active tab with current route
  useEffect(() => {
    const path = location.pathname.split('/banking/')[1] || 'home';
    setActiveTab(path.includes('/') ? path.split('/')[0] : path);
  }, [location]);

  const handleNavigation = (path) => {
    setActiveTab(path);
    navigate(`/banking/${path}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Redirect to home if root banking path is accessed
  useEffect(() => {
    if (user === undefined) return; 

    if (user === null) {
      navigate('/login', { replace: true });
    } else if (user?.forcePasswordChangedFlag) {
      navigate('/change-password', { replace: true });
    }else if (location.pathname === '/banking') {
      navigate('/banking/home', { replace: true });
    }
  }, [user, location.pathname, navigate]);

  if (user === undefined) return null;

  return (
    <div style={{ 
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div className="master-page flex flex-col min-h-screen">
        <Header
          user={user}
          activeTab={activeTab}
          onNavigate={handleNavigation}
          onLogout={handleLogout}
        />
        
        <main className="main-content flex-grow p-4">
          <Outlet />
        </main>
        
        <Footer />
        <ChatBot />

        <Modal
          isOpen={!!error}
          onClose={() => setError(null)}
          title="Error"
          message={error}
        />
        
        <Modal
          isOpen={!!success}
          onClose={() => setSuccess(null)}
          title="Success"
          message={success}
        />
      </div>
    </div>
  );
};

export default MasterPage;