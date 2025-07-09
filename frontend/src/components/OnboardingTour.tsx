import React from 'react';
import Joyride, { CallBackProps, Step } from 'react-joyride';

interface OnboardingTourProps {
  steps: Step[];
  run: boolean;
  onClose: () => void;
}

const OnboardingTour: React.FC<OnboardingTourProps> = ({ steps, run, onClose }) => {
  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showSkipButton
      showProgress
      disableScrolling
      styles={{
        options: {
          zIndex: 10000,
          primaryColor: '#3182ce',
          textColor: '#222',
          arrowColor: '#3182ce',
        },
      }}
      locale={{
        back: 'Back',
        close: 'Close',
        last: 'Finish',
        next: 'Next',
        skip: 'Skip',
      }}
      callback={(data: CallBackProps) => {
        if (data.status === 'finished' || data.status === 'skipped') {
          onClose();
        }
      }}
    />
  );
};

export default OnboardingTour; 