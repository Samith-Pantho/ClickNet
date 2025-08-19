import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useBanking } from '../../contexts/BankingContext';
import AccountCard from '../../components/banking/AccountCard';
import Modal from '../../components/common/Modal';
import AdModal from '../../components/common/AdModal';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';

const HomePage = () => {
  const { user, updateAdvertisements } = useAuth();
  const { accounts, loading, loadAccounts } = useBanking();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAdPopup, setShowAdPopup] = useState(true);
  // Memoized data loading function
  const fetchData = useCallback(async () => {
    try {
      await loadAccounts();
    } catch (err) {
      setError(err.message || 'Failed to load accounts');
    }
  }, [loadAccounts]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Slider configurations
  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: false,
    adaptiveHeight: true
  };

  const adSliderSettings = {
    ...sliderSettings,
    autoplaySpeed: 5000,
  };

  // Filter active advertisements
  const activeAds = user?.advertisements?.filter(ad => ad.STATUS) || [];

  const handleAdvertisment = () => {
    setShowAdPopup(false);
    updateAdvertisements();
  }

  return (
    <div className="home-page">
      {loading && <LoadingSpinner />}
      
      {/* Main Slider */}
      <div className="main-slider mb-8">
        <Slider {...sliderSettings}>
          <div>
            <img 
              src="/assets/images/slide1.jpg" 
              alt="Banking Services" 
            />
          </div>
          <div>
            <img 
              src="/assets/images/slide2.jpg" 
              alt="Online Banking" 
            />
          </div>
          <div>
            <img 
              src="/assets/images/slide3.jpg" 
              alt="Secure Transactions" 
            />
          </div>
        </Slider>
      </div>
      
      {/* Accounts by Category */}
      <div className="accounts-section">
        <h2 className="center-text-align font-bold">Accounts</h2>
        {accounts && Object.keys(accounts).length > 0 ? (
          <div className="account-cards-container">
            <div className="account-cards-grid">
              {Object.values(accounts)
                .flat()
                .map(account => (
                  <AccountCard 
                    key={account.account_number} 
                    account={account} 
                    onClick={() => navigate(`/banking/account/${account.account_number}`)}
                  />
                ))
              }
            </div>
          </div>
        ): (
          <div className="text-center py-8">
            <p className="text-gray-500">No accounts found</p>
          </div>
        )}
      </div>
      
      <AdModal 
        isOpen={showAdPopup}
        onClose={() => handleAdvertisment()}
        ads={activeAds}
        sliderSettings={adSliderSettings}
      />
      
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
  );
};

export default HomePage;