import React from 'react';
import '../../CSS/ProgressSteps.css';

const ProgressSteps = ({ steps, currentStep }) => {
  let hasFailed = false;
  return (
    <div className="progress-steps">
      {steps.map((step, index) => {
        if (hasFailed) {
          step.status = 'failed';
        }

        const status = 
          step.status === 'failed' ? 'failed' :
          step.status === 'completed' ? 'completed' : 
          step.id === currentStep ? 'active' :
          step.id < currentStep ? 'completed' : '';
          
        if (status === 'failed') {
          hasFailed = true;
        }
        return (
          <div key={step.id} className={`step ${status}`}>
            <div className="step-number">
              {status === 'completed' ? (
                <span className="checkmark">✓</span>
              ) : status === 'failed' ? (
                <span className="failed-mark">✕</span>
              ) : (
                step.id
              )}
            </div>
            {index < steps.length && (
              <div className={`step-connector ${status === 'completed' ? 'completed' : ''}`}></div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ProgressSteps;