import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getBranches, sendMobileOTP, verifyMobileOTP, sendEmailOTP, verifyEmailOTP, initialize } from '../services/kycService';
import { useAuth } from '../contexts/AuthContext';
import OTPModal from '../components/common/OTPModal';
import '../CSS/BranchAndContact.css';

const BranchAndContact = ({ onNext, onPrev, formData, updateFormData, showModal, isLoading, setIsLoading, updateStepStatus }) => {
    const navigate = useNavigate();
    const { setAuthState } = useAuth();
    const [branches, setBranches] = useState([]);
    const [phoneNumber, setPhoneNumber] = useState('');
    const [email, setEmail] = useState('');
    const [mobileVerified, setMobileVerified] = useState(false);
    const [emailVerified, setEmailVerified] = useState(false);
    const [showMobileOTPModal, setShowMobileOTPModal] = useState(false);
    const [showEmailOTPModal, setShowEmailOTPModal] = useState(false);
    const [modal, setModal] = useState({
            title: '',
            content: ''
        });
    
    const [filterText, setFilterText] = useState('');

    if(modal.title !== '' && modal.content !== ''){
        showModal(modal.title, modal.content)
    }
  

    useEffect(() => {
        const fetchBranches = async () => {
        try {
            setIsLoading(true);
            const response = await getBranches();
            if (response.Status === 'OK') {
            setBranches(response.Result);
            } else {
             setModal(modal.title = 'Error', modal.content = response.Message);
            }
        } catch (err) {
             setModal(modal.title = 'Error', modal.content = 'Failed to fetch branches');
        } finally {
            setIsLoading(false);
        }
        };

        fetchBranches();
    }, [modal, setIsLoading]);

    const handleBranchChange = (e) => {
        updateFormData({ branch_code: e.target.value });
    };

    const handleSendMobileOTP = async () => {
        try {
            setIsLoading(true);
            const response = await sendMobileOTP(phoneNumber);
            if (response.Status === 'OTP') {
                setShowMobileOTPModal(true);
            } else {
                showModal('Error', response.Message);
            }
        } catch (err) {
            showModal('Error', 'Failed to send OTP to mobile');
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerifyMobileOTP = async (otp) => {
        try {
            setIsLoading(true);
            const response = await verifyMobileOTP(phoneNumber, otp);
            if (response.Status === 'OK') {
                setMobileVerified(true);
                updateFormData({ phone_number: phoneNumber });
                setShowMobileOTPModal(false);
                showModal('Success', 'Mobile number verified successfully');
            } else {
                showModal('Error', response.Message);
            }
        } catch (err) {
            showModal('Error', 'Failed to verify mobile OTP');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSendEmailOTP = async () => {
        try {
            setIsLoading(true);
            const response = await sendEmailOTP(email);
            if (response.Status === 'OTP') {
                setShowEmailOTPModal(true);
            } else {
                showModal('Error', response.Message);
            }
        } catch (err) {
            showModal('Error', 'Failed to send OTP to email');
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerifyEmailOTP = async (otp) => {
        try {
            setIsLoading(true);
            const response = await verifyEmailOTP(email, otp);
            if (response.Status === 'OK') {
                setEmailVerified(true);
                updateFormData({ email_address: email });
                setShowEmailOTPModal(false);
                showModal('Success', 'Email verified successfully');
        } else {
            showModal('Error', response.Message);
        }
        } catch (err) {
            showModal('Error', 'Failed to verify email OTP');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async () => {
        if (!formData.branch_code) {
        showModal('Error', 'Please select a branch');
        return;
        }

        if (!mobileVerified) {
        showModal('Error', 'Please verify your mobile number');
        return;
        }

        try {
            setIsLoading(true);
            const response = await initialize(formData);
        if (response.Status === 'OK') {
            setAuthState({
            accessToken: response.Result.access_token,
            customerData: response.Result.customer_data
            });
            console.log(response.Result.access_token);

            if(response.Result.customer_data?.IS_TAX_ID_VERIFIED){
                navigate('/', { state: { currentStep: 4 } });
            }
            else{
                onNext();
            }
        } else {
            showModal('Error', response.Message);
        }
        } catch (err) {
            console.log(err)
            showModal('Error', "Failed to Initialize KYC");
        } finally {
            setIsLoading(false);
        }
    };

     const filteredBranches = branches.filter(branch => {
        const search = filterText.toLowerCase();
        return branch.branch_name.toLowerCase().includes(search)
    });


    return (
        <div className="selection-container">
            <div className="selection-header">    
                <h2>Branch and Contact Details</h2>
                <p>Please provide your branch and contact information</p>
            </div>
        
        <div className="form-group">
            <label htmlFor="branchFilter">Filter Branches (Name, Place, Region)</label>
            <input
                type="text"
                id="branchFilter"
                className="form-control mb-2"
                placeholder="Type to filter branches..."
                value={filterText}
                onChange={e => setFilterText(e.target.value)}
            />

            <label htmlFor="branch">Select Branch</label>
            <select
                id="branch"
                value={formData.branch_code}
                onChange={handleBranchChange}
                className="form-control"
            >
                <option value="">Select a branch</option>
                {filteredBranches.map(branch => (
                <option key={branch.branch_code} value={branch.branch_code}>
                    {branch.branch_code} - {branch.branch_name}
                </option>
                ))}
            </select>
        </div>
        
        <div className="form-group">
            <label htmlFor="phone">Mobile Number</label>
            <div className="input-with-button">
            <input
                type="tel"
                id="phone"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                className="form-control"
                placeholder="Enter mobile number"
                disabled={mobileVerified}
            />
            {!mobileVerified && (
                <button 
                onClick={handleSendMobileOTP} 
                className="verify-button"
                disabled={!phoneNumber}
                >
                Verify Now
                </button>
            )}
            {mobileVerified && (
                <span className="verified-badge">Verified</span>
            )}
            </div>
        </div>
        
        <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-with-button">
            <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-control"
                placeholder="Enter email address"
                disabled={emailVerified}
            />
            {!emailVerified && (
                <button 
                onClick={handleSendEmailOTP} 
                className="verify-button"
                disabled={!email}
                >
                Verify Now
                </button>
            )}
            {emailVerified && (
                <span className="verified-badge">Verified</span>
            )}
            </div>
        </div>
        
        <div className="step-actions">
            <button onClick={onPrev} className="button button-secondary">Back</button>
            <button 
            onClick={handleSubmit} 
            className="button button-primary"
            disabled={!formData.branch_code || !mobileVerified}
            >
            Submit
            </button>
        </div>
        
        <OTPModal
            isOpen={showMobileOTPModal}
            onClose={() => setShowMobileOTPModal(false)}
            onSubmit={handleVerifyMobileOTP}
            isLoading={isLoading}
        />
        
        <OTPModal
            isOpen={showEmailOTPModal}
            onClose={() => setShowEmailOTPModal(false)}
            onSubmit={handleVerifyEmailOTP}
            isLoading={isLoading}
        />
        </div>
    );
};

export default BranchAndContact;