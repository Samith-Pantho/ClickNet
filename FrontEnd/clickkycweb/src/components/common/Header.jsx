import React from 'react';
import '../../CSS/Header.css';
import logo from '../../assets/images/clicknet-logo.png';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-container">
          <img src={logo} alt="ClickNet Logo" className="logo" />
          <span className="brand-name">ClickKYC</span>
        </div>
      </div>
    </header>
  );
};

export default Header;