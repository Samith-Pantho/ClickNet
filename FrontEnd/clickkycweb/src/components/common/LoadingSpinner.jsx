import React from 'react';
import '../../CSS/LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-overlay">
      <img 
        src="/assets/images/loading.gif" 
        alt="Loading..." 
        className="loading-gif"
      />
    </div>
  );
};

export default LoadingSpinner;