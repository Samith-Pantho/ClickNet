import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/images/clicknet-logo.png';
import {capitalizeName} from '../../utils/helpers'

const Header = ({ user, activeTab, onNavigate, onLogout }) => {
  const navigate = useNavigate();
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const popupRef = useRef(null);
  const profileRef = useRef(null);

  // Handle outside clicks
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target) &&
          profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfilePopup(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleProfilePopup = () => {
    setShowProfilePopup(!showProfilePopup);
  };

  const handleNavigation = (path) => {
    if (!user) {
      navigate('/login', { replace: true });
      return;
    }
    onNavigate(path);
    navigate(`/banking/${path}`);
  };

  return (
    <header className="header">
      <div className="logo-container">
        <img src={logo} alt="ClickNet Logo" className="logo" />
      </div>
      
      <div className="nav-container">
        <nav className="main-nav">
          <ul>
            {['home', 'transfer', 'addMoney', 'history', 'activity', 'profile', 'complaints'].map((tab) => {
              const displayName =
                tab === 'addMoney'
                  ? 'Add Money'
                  : tab.charAt(0).toUpperCase() + tab.slice(1);

              return (
                <li key={tab} className={activeTab === tab ? 'active' : ''}>
                  <button onClick={() => handleNavigation(tab)}>
                    {displayName}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
      
      <div 
        className="user-profile-container"
        ref={profileRef}
      >
        <div 
          className="user-profile" 
          onClick={toggleProfilePopup}
        >
          <div className="profile-container">
            <img 
              src={user?.profile_picture} 
              alt="Profile" 
              className="profile-pic"
            />
            <span className="user-name">{user?.fullName}</span>
          </div>
          
          {showProfilePopup && (
            <div 
              className="profile-popup"
              ref={popupRef}
            >
              <div className="popup-header">
                <img 
                  src={user?.profile_picture} 
                  alt="Profile" 
                  className="popup-profile-pic"
                  onClick={() => handleNavigation('profile')}
                />
                <button 
                  className="edit-pic-btn"
                  onClick={() => handleNavigation('profile')}
                >
                  Edit
                </button>
              </div>
              <div className="popup-content">
                <p className="greeting">Hi, {user?.fullName?.split(' ').map(part => capitalizeName(part)).join(' ')}!</p>
                <button 
                  className="manage-profile-btn"
                  onClick={() => handleNavigation('profile')}
                >
                  Manage your profile
                </button>
              </div>
              <div className="popup-footer">
                <button 
                  className="logout-btn"
                  onClick={() => {
                    onLogout();
                    setShowProfilePopup(false);
                  }}
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;