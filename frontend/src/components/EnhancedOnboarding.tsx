import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import * as api from '../api';
import { useTranslation } from 'react-i18next';

// Lucide/Heroicons SVGs for icons
const CheckCircleIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="text-green-500"><circle cx="10" cy="10" r="9" /><polyline points="7 10.5 9.5 13 13 8.5" /></svg>
);
const InfoIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="text-blue-500"><circle cx="10" cy="10" r="9" /><line x1="10" y1="14" x2="10" y2="10" /><circle cx="10" cy="7" r="1" /></svg>
);
const StarIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="currentColor" className="text-yellow-400"><polygon points="10 2 12.59 7.36 18.51 8.09 14 12.26 15.18 18.09 10 15.27 4.82 18.09 6 12.26 1.49 8.09 7.41 7.36 10 2" /></svg>
);
const ArrowForwardIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="10" x2="15" y2="10" /><polyline points="10 5 15 10 10 15" /></svg>
);

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
  demo?: boolean;
  action?: () => void;
}

interface OnboardingProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const EnhancedOnboarding: React.FC<OnboardingProps> = ({ isOpen, onClose, onComplete }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [demoJobCreated, setDemoJobCreated] = useState(false);
  const [demoResults, setDemoResults] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<string>('');
  const [toastMsg, setToastMsg] = useState<{title: string, description: string, status: string, duration: number} | null>(null);

  const onboardingSteps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: t('onboarding.welcomeTitle', 'Welcome to LeadTap! 🚀'),
      description: t('onboarding.welcomeDescription', "Let's get you set up with your first lead generation campaign in just a few minutes."),
      completed: false,
      required: true,
    },
    {
      id: 'demo-job',
      title: t('onboarding.createFirstJobTitle', 'Create Your First Job'),
      description: t('onboarding.createFirstJobDescription', "We'll create a sample job to show you how LeadTap works."),
      completed: false,
      required: true,
      demo: true,
      action: async () => {
        try {
          // Create a demo job with sample data
          const demoQueries = [t('onboarding.demoQuery1', 'restaurants in New York'), t('onboarding.demoQuery2', 'coffee shops in San Francisco')];
          const response = await api.createJob(demoQueries);
          setDemoJobCreated(true);
          setToastMsg({
            title: t('onboarding.demoJobCreated', 'Demo Job Created!'),
            description: t('onboarding.demoJobDescription', 'We\'ve created a sample job with queries like "restaurants in New York" and "coffee shops in San Francisco".'),
            status: 'success',
            duration: 3000,
          });
        } catch (error) {
          setToastMsg({
            title: t('onboarding.demoCreationFailed', 'Demo Creation Failed'),
            description: t('onboarding.demoCreationFailedDescription', "We'll continue with the tour anyway."),
            status: 'warning',
            duration: 3000,
          });
        }
      }
    },
    {
      id: 'view-results',
      title: t('onboarding.viewResultsTitle', 'View Your Results'),
      description: t('onboarding.viewResultsDescription', 'See how LeadTap extracts detailed business information automatically.'),
      completed: false,
      required: true,
      demo: true,
    },
    {
      id: 'export-data',
      title: t('onboarding.exportDataTitle', 'Export Your Data'),
      description: t('onboarding.exportDataDescription', 'Download your leads in multiple formats for your CRM or marketing tools.'),
      completed: false,
      required: true,
      demo: true,
      action: () => {
        setToastMsg({
          title: t('onboarding.exportSuccessful', 'Export Successful!'),
          description: t('onboarding.exportSuccessfulDescription', 'Your data has been exported in CSV format.'),
          status: 'success',
          duration: 3000,
        });
      }
    },
    {
      id: 'crm-setup',
      title: t('onboarding.crmSetupTitle', 'Setup Your CRM'),
      description: t('onboarding.crmSetupDescription', 'Import your leads into your CRM or use our built-in lead management.'),
      completed: false,
      required: false,
      demo: true,
    },
    {
      id: 'complete',
      title: t('onboarding.readyToGoTitle', "You're Ready to Go! 🎉"),
      description: t('onboarding.readyToGoDescription', 'Start creating real jobs and generating leads for your business.'),
      completed: false,
      required: true,
    }
  ];

  const [steps, setSteps] = useState(onboardingSteps);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      // Mark current step as completed
      const updatedSteps = [...steps];
      updatedSteps[currentStep].completed = true;
      setSteps(updatedSteps);
      
      // Execute step action if exists
      if (steps[currentStep].action) {
        steps[currentStep].action!();
      }
      
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Mark all steps as completed
    const updatedSteps = steps.map(step => ({ ...step, completed: true }));
    setSteps(updatedSteps);
    
    // Save onboarding completion
    localStorage.setItem('onboarding_complete', 'true');
    localStorage.setItem('onboarding_feedback', feedback);
    
    setToastMsg({
      title: t('onboarding.onboardingComplete', 'Onboarding Complete!'),
      description: t('onboarding.onboardingCompleteDescription', 'Welcome to LeadTap. Start generating leads now!'),
      status: 'success',
      duration: 5000,
    });
    
    onComplete();
    onClose();
  };

  const getProgressPercentage = () => {
    const completedSteps = steps.filter(step => step.completed).length;
    return (completedSteps / steps.length) * 100;
  };

  const currentStepData = steps[currentStep];

  // Replace Chakra UI Modal with ShadCN Dialog
  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-2xl mx-4 animate-fade-in">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <span className="text-lg font-bold">{currentStepData.title}</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-semibold">
                {t('onboarding.step', 'Step')} {currentStep + 1} {t('onboarding.of', 'of')} {steps.length}
              </span>
            </div>
            <div className="px-6 py-4 space-y-6">
              {/* Progress Bar */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-300">{t('onboarding.progress', 'Progress')}</span>
                  <span className="text-sm text-gray-600 dark:text-gray-300">{Math.round(getProgressPercentage())}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                  <div className="bg-blue-600 h-2.5 rounded-full transition-all" style={{ width: `${getProgressPercentage()}%` }} />
                </div>
              </div>
              {/* Step Description */}
              <span className="text-gray-600 dark:text-gray-300 text-md">{currentStepData.description}</span>
              {/* Demo Content */}
              {currentStepData.demo && (
                <div>
                  {currentStepData.id === 'demo-job' && (
                    <div className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-md">
                      <InfoIcon className="w-5 h-5 mr-2 mt-1" />
                      <div>
                        <span className="font-semibold">{t('onboarding.demoJobCreated', 'Demo Job Created!')}</span>
                        <div className="text-sm text-gray-700 dark:text-gray-300">{t('onboarding.demoJobDescription', 'We\'ve created a sample job with queries like "restaurants in New York" and "coffee shops in San Francisco".')}</div>
                      </div>
                    </div>
                  )}
                  {currentStepData.id === 'view-results' && demoResults.length > 0 && (
                    <div className="border border-gray-200 rounded-md p-4">
                      <span className="font-bold mb-3 block">{t('onboarding.sampleResults', 'Sample Results:')}</span>
                      <div className="space-y-2">
                        {demoResults.slice(0, 3).map((result, index) => (
                          <div key={index} className="p-3 bg-gray-50 rounded-md">
                            <span className="font-bold">{result.business_name}</span>
                            <span className="block text-sm text-gray-600">{result.address}</span>
                            <div className="flex space-x-4 mt-1">
                              {/* Add more fields as needed */}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {/* Feature Tips */}
              {currentStepData.id === 'complete' && (
                <div>
                  <span className="font-bold mb-3 block">{t('onboarding.proTips', 'Pro Tips:')}</span>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <StarIcon className="w-4 h-4 mr-2 text-yellow-500" />
                      <span className="text-sm">{t('onboarding.specificQueries', 'Use specific queries for better results')}</span>
                    </div>
                    <div className="flex items-center">
                      <StarIcon className="w-4 h-4 mr-2 text-yellow-500" />
                      <span className="text-sm">{t('onboarding.exportRegularly', 'Export data regularly to your CRM')}</span>
                    </div>
                    <div className="flex items-center">
                      <StarIcon className="w-4 h-4 mr-2 text-yellow-500" />
                      <span className="text-sm">{t('onboarding.upgradeToPro', 'Upgrade to Pro for advanced features')}</span>
                    </div>
                  </div>
                </div>
              )}
              {/* Feedback (final step) */}
              {currentStepData.id === 'complete' && (
                <div className="space-y-2">
                  <label htmlFor="onboarding-feedback" className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('onboarding.howWasExperience', 'How was your onboarding experience?')}</label>
                  <textarea id="onboarding-feedback" className="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-2 text-sm" value={feedback} onChange={e => setFeedback(e.target.value)} />
                </div>
              )}
            </div>
            <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <button onClick={handlePrevious} disabled={currentStep === 0} className="inline-flex items-center px-4 py-2 rounded-md bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                {t('onboarding.previous', 'Previous')}
              </button>
              <div className="flex space-x-2">
                <button onClick={onClose} className="inline-flex items-center px-4 py-2 rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-200 font-medium">
                  {t('onboarding.close', 'Close')}
                </button>
                <button onClick={handleNext} className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                  {currentStep === steps.length - 1 ? t('onboarding.finish', 'Finish') : t('onboarding.next', 'Next')}
                  <ArrowForwardIcon className="w-4 h-4 ml-2" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {toastMsg && (
        <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 bg-${toastMsg.status}-500 text-white px-4 py-2 rounded-md shadow-lg z-50`}>
          <div className="flex items-center">
            <span className="mr-2">{toastMsg.title}</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div className="mt-1 text-sm">{toastMsg.description}</div>
        </div>
      )}
    </>
  );
};

export default EnhancedOnboarding; 