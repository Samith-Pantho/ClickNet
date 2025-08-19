import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { uploadProfilePicture } from '../../services/bankingService';
import LoadingSpinner from './LoadingSpinner';
import Modal from './Modal';

const ProfilePictureUpload = ({ isOpen, onClose }) => {
  const { user, updateProfilePicture , loadProfilePicture } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    setLoading(true);
    try {
      const response = await uploadProfilePicture(selectedFile);
      
      if (response.data.Status === 'OK') {
        setSuccess(response.data.Message || 'Profile picture updated successfully');
        const imgResponse = await loadProfilePicture();
        // Update user context with new picture
        updateProfilePicture(imgResponse);
        // Clear the selected file and preview after successful upload
        setSelectedFile(null);
        setPreview(null);
      } else {
        setError(response.data.Message || 'Failed to update profile picture');
      }
    } catch (err) {
      setError(err.response?.data?.Message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay">
        <div className="modal-container profilepic-model-bg">
          <div className="modal-content">
            <div className="modal-close-btn">
              <button 
                onClick={onClose} 
                className="close-btn"
              >
                &times;
              </button>
            </div>
            <div className="modal-header">
              <h3 className="modal-title">Update Profile Picture</h3>
            </div>
            <div className="modal-body">
              {loading && <LoadingSpinner />}
              
              <div className="preview">
                <img 
                  src={preview || user?.profile_picture} 
                  alt="Profile Preview" 
                />
              </div>
              
              <form onSubmit={handleSubmit} className="mt-4">
                <div className="form-group">
                  <label htmlFor="profilePicture" className="block mb-2 font-medium">
                    Select New Picture
                  </label>
                  <input
                    type="file"
                    id="profilePicture"
                    accept="image/*"
                    onChange={handleFileChange}
                    required
                    className="w-full p-2 border rounded"
                  />
                </div>
                
                <div className="form-actions mt-4">
                  <button 
                    type="submit" 
                    disabled={!selectedFile || loading}
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Uploading...' : 'Upload Picture'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Modal
        isOpen={!!error}
        onClose={() => setError(null)}
        title="Error"
        message={error}
      />
      
      <Modal
        isOpen={!!success}
        onClose={() => {
          setSuccess(null);
          onClose(); // Close the upload modal after success
        }}
        title="Success"
        message={success}
      />
    </>
  );
};

export default ProfilePictureUpload;