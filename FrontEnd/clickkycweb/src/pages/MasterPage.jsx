import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ConfigContext } from '../contexts/ConfigContext';
import { useAuth } from '../contexts/AuthContext';
import ProgressSteps from '../components/common/ProgressSteps';
import ProductSelection from './ProductSelectionPage';
import BranchAndContact from './BranchAndContactPage';
import Verification from './VerificationPage';
import CustomerInformation from './CustomerInformationPage';
import Final from './FinalPage';
import Modal from '../components/common/Modal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import '../CSS/Master.css';
import backgroundImage from '../assets/images/Bg.png'; 

const ClickKYC = () => {
  // eslint-disable-next-line no-unused-vars
  const { config } = useContext(ConfigContext);
  const { authState } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [modal, setModal] = useState({ isOpen: false, title: '', message: '' });
  const [formData, setFormData] = useState({
    product_code: '',
    branch_code: '',
    phone_number: '',
    email_address: '',
  });
  const [stepStatus, setStepStatus] = useState({});
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.currentStep) {
      setCurrentStep(location.state.currentStep);
    }
  }, [location.state]);

  useEffect(() => {
    if (currentStep === 1) {
      setIsLoading(false);
      setModal({ isOpen: false, title: '', message: '' });
      setFormData({
        product_code: '',
        branch_code: '',
        phone_number: '',
        email_address: '',
      });
      setStepStatus({});
    }
  }, [currentStep]);

  const steps = [
    { id: 1, name: 'Product' },
    { id: 2, name: 'Contact' },
    { id: 3, name: 'Verification' },
    { id: 4, name: 'Customer Info' },
    { id: 5, name: 'Final' },
  ];

  const updateStepStatus = (stepId, status) => {
    setStepStatus(prev => {
      const newStatus = { ...prev, [stepId]: status };
      return newStatus;
    });
  };

  const handleNextStep = () => {
    if (currentStep < steps.length) {
      updateStepStatus(currentStep, 'completed');
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      navigate('.', { state: { currentStep: nextStep }, replace: true });
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      const prevStep = currentStep - 1;
      setCurrentStep(prevStep);
      navigate('.', { state: { currentStep: prevStep }, replace: true });
    }
  };

  const updateFormData = (newData) => {
    setFormData(prev => ({ ...prev, ...newData }));
  };

  const showModal = (title, message) => {
    setModal({ isOpen: true, title, message });
  };

  const closeModal = () => {
    setModal({ ...modal, isOpen: false });
  };

  const getEnhancedSteps = () => {
    return steps.map(step => ({
      ...step,
      status: stepStatus[step.id] || (step.id < currentStep ? 'completed' : '')
    }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <ProductSelection
            onNext={handleNextStep}
            updateFormData={updateFormData}
            showModal={showModal}
            setIsLoading={setIsLoading}
            updateStepStatus={updateStepStatus} 
          />
        );
      case 2:
        return (
          <BranchAndContact
            onNext={handleNextStep}
            onPrev={handlePrevStep}
            formData={formData}
            updateFormData={updateFormData}
            showModal={showModal}
            setIsLoading={setIsLoading}
            isLoading={isLoading}
            updateStepStatus={updateStepStatus}
          />
        );
      case 3:
        return (
          <Verification
            onNext={handleNextStep}
            onPrev={handlePrevStep}
            showModal={showModal}
            setIsLoading={setIsLoading}
            accessToken={authState.accessToken}
            updateStepStatus={updateStepStatus}
          />
        );
      case 4:
        return (
          <CustomerInformation
            onNext={handleNextStep}
            onPrev={handlePrevStep}
            showModal={showModal}
            setIsLoading={setIsLoading}
            accessToken={authState.accessToken}
            updateStepStatus={updateStepStatus}
          />
        );
      case 5:
        return (
          <Final
            showModal={showModal}
            setIsLoading={setIsLoading}
            updateStepStatus={updateStepStatus}
          />
        );
      default:
        return <ProductSelection />;
    }
  };

  return (
    <div className="master-container" style={{ 
      backgroundImage: `url(${backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div className="main-content">
        {isLoading && <LoadingSpinner />}
        
        <ProgressSteps steps={getEnhancedSteps()} currentStep={currentStep} />
        
        <div className="step-container">
          {renderStep()}
        </div>

        <Modal
          isOpen={modal.isOpen}
          onClose={closeModal}
          title={modal.title}
          message={modal.message}
        />
      </div>
    </div>
  );
};

export default ClickKYC;