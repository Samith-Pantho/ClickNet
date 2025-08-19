import React from 'react';
import Slider from 'react-slick';

const AdModal = ({ isOpen, onClose, ads, sliderSettings }) => {
  if (!isOpen || ads.length === 0) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="ad-modal-content">
          <div className="modal-close-btn">
            <button 
              onClick={onClose} 
              className="close-btn"
            >
              &times;
            </button>
          </div>
          <div className="ad-modal-body">
            <Slider {...sliderSettings}>
              {ads.map((ad) => (
                <div key={ad.SL} className="ad-modal-slide">
                  {ad.IMAGE_URL ? (
                    <div
                      className="ad-image-container"
                      onClick={() => ad.TARGET_URL && window.open(ad.TARGET_URL, '_blank')}
                    >
                      <img
                        src={ad.IMAGE_URL}
                        alt={ad.TITLE}
                        className="ad-image"
                      />
                    </div>
                  ) : (
                    <div className="text-ad">
                      <h4 className="ad-title">{ad.TITLE}</h4>
                      {ad.TARGET_URL && (
                        <a
                          href={ad.TARGET_URL}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Learn More
                        </a>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </Slider>
          </div>
          <div className="modal-footer">
            <button 
              onClick={onClose} 
              className={"button button-primary bg-gray-500 hover:bg-gray-600 text-white transition-colors"}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdModal;