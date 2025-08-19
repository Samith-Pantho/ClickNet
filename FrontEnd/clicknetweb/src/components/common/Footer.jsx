import React from 'react';

const Footer = () => {
  const contactInfo = [
    'ClickNet Service © 2025',
    'Customer Support: 24/7 Helpline +1234567890',
    'Email: serviceclicknet@gmail.com'
  ];

  return (
    <footer className="footer">
      <div className="footer-content">
        {contactInfo.map((info, index) => (
          <span key={index} className="footer-item">
            {info} &nbsp; | &nbsp;
          </span>
        ))}
      </div>
    </footer>
  );
};

export default Footer;