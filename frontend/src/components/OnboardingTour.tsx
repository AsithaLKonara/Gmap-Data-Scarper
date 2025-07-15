import React, { useState } from 'react';
import Joyride, { CallBackProps, Step } from 'react-joyride';

interface OnboardingTourProps {
  steps: Step[];
  run: boolean;
  onClose: () => void;
}

export const MODULE_TOURS: { [key: string]: Step[] } = {
  dashboard: [
    { target: '.dashboard-widget', content: 'This is your dashboard. You can customize widgets here.' },
    { target: '.fab-add-lead', content: 'Use this button to quickly add a new lead.' },
  ],
  leads: [
    { target: '.lead-table', content: 'Here you can view and manage all your leads.' },
    { target: '.lead-filter', content: 'Filter leads by status, owner, or score.' },
  ],
  // Add more module tours as needed
};

export const OnboardingTour: React.FC<OnboardingTourProps> = ({ steps, run, onClose }) => {
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

interface ChecklistItem {
  key: string;
  label: string;
  completed: boolean;
}

export const OnboardingChecklist: React.FC<{
  items: ChecklistItem[];
  onStartTour: (key: string) => void;
}> = ({ items, onStartTour }) => (
  <div className="bg-card border border-border rounded-lg p-6 shadow-md max-w-md mx-auto">
    <h2 className="text-lg font-bold mb-4">Onboarding Checklist</h2>
    <ul className="space-y-3">
      {items.map(item => (
        <li key={item.key} className="flex items-center justify-between">
          <span className={item.completed ? 'line-through text-muted-foreground' : ''}>{item.label}</span>
          <button
            className={`ml-4 px-3 py-1 rounded text-sm font-medium ${item.completed ? 'bg-green-100 text-green-700' : 'bg-primary text-primary-foreground hover:bg-primary/90'}`}
            onClick={() => onStartTour(item.key)}
            disabled={item.completed}
          >
            {item.completed ? 'Done' : 'Start'}
          </button>
        </li>
      ))}
    </ul>
  </div>
);

export default OnboardingTour; 