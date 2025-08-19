import React from 'react';

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