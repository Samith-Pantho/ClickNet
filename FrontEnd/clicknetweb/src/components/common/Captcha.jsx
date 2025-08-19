import React, { useState, useEffect, useContext, forwardRef, useImperativeHandle, useRef } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';
import { ConfigContext } from '../../contexts/ConfigContext';
import LoadingSpinner from './LoadingSpinner';

const CaptchaComponent = forwardRef(({ onChange }, ref) => {
  const config = useContext(ConfigContext);
  const [siteKey, setSiteKey] = useState(null);
  const recaptchaRef = useRef(null);

  useEffect(() => {
    const fetchedKey = config?.GOOGLE_RECAPTCHA_SITE_KEY;
    if (fetchedKey) setSiteKey(fetchedKey.trim());
  }, [config?.GOOGLE_RECAPTCHA_SITE_KEY]);

  useImperativeHandle(ref, () => ({
    reset() {
      recaptchaRef.current?.reset();
    }
  }));

  if (!siteKey) {
    return <LoadingSpinner />;
  }

  return (
    <ReCAPTCHA
      ref={recaptchaRef}
      sitekey={siteKey}
      onChange={onChange}
    />
  );
});

export default CaptchaComponent;
