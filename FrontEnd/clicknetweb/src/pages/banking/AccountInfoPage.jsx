import React from 'react';
import { useParams } from 'react-router-dom';
import AccountDetails from '../../components/banking/AccountDetails';

const AccountInfoPage = () => {
  const { accountNumber } = useParams();

  return (
    <div className="account-info-page">
      <AccountDetails accountNumber={accountNumber} />
    </div>
  );
};

export default AccountInfoPage;