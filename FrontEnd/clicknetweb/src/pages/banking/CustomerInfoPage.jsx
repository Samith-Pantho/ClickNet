import React, { useState } from 'react';
import CustomerInfo from '../../components/banking/CustomerInfo';
import ProfilePictureUpload from '../../components/common/ProfilePictureUpload';

const CustomerInfoPage = () => {
  const [showUploadModal, setShowUploadModal] = useState(false);

  return (
    <div className="customer-info-page">
      <CustomerInfo 
        onEditPicture={() => setShowUploadModal(true)} 
      />

      <ProfilePictureUpload 
        isOpen={showUploadModal} 
        onClose={() => setShowUploadModal(false)} 
      />
    </div>
  );
};

export default CustomerInfoPage;