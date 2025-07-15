import React from 'react';
import {
  SearchIcon,
  DownloadIcon,
  LockIcon,
  StarIcon,
  CheckCircleIcon,
  TimeIcon
} from '@chakra-ui/icons';
import { useTranslation } from 'react-i18next';

const About = () => {
  const { t } = useTranslation();
  const features = [
    {
      icon: SearchIcon,
      title: t('about.features.advancedSearch.title', 'Advanced Search'),
      description: t('about.features.advancedSearch.description', 'Powerful search capabilities with location-based filtering and custom queries')
    },
    {
      icon: DownloadIcon,
      title: t('about.features.multipleExportFormats.title', 'Multiple Export Formats'),
      description: t('about.features.multipleExportFormats.description', 'Export your data in CSV, JSON, Excel, and other popular formats')
    },
    {
      icon: LockIcon,
      title: t('about.features.secureReliable.title', 'Secure & Reliable'),
      description: t('about.features.secureReliable.description', 'Enterprise-grade security with 99.9% uptime and data protection')
    },
    {
      icon: StarIcon,
      title: t('about.features.premiumQuality.title', 'Premium Quality'),
      description: t('about.features.premiumQuality.description', 'High-quality, accurate data extraction with validation and verification')
    },
    {
      icon: CheckCircleIcon,
      title: t('about.features.easyToUse.title', 'Easy to Use'),
      description: t('about.features.easyToUse.description', 'No coding required. Simple interface for users of all skill levels')
    },
    {
      icon: TimeIcon,
      title: t('about.features.realTimeUpdates.title', 'Real-time Updates'),
      description: t('about.features.realTimeUpdates.description', 'Access the latest business information and contact details')
    }
  ];

  return (
    <div className="py-20 min-h-[calc(100vh-64px)]">
      <div className="max-w-[1200px] mx-auto">
        <div className="flex flex-col gap-16">
          <div className="flex flex-col gap-6 text-center">
            <h1 className="text-5xl font-bold gradient-text">
              {t('about.heading', 'About LeadTap')}
            </h1>
            <p className="text-gray-400 text-xl max-w-[800px] mx-auto leading-relaxed">
              {t('about.description', 'LeadTap is a powerful Google Maps data extraction platform designed to help businesses, researchers, and marketers gather comprehensive location data efficiently and accurately. Our advanced technology makes it easy to extract business information, contact details, and location data from Google Maps.')}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComp = feature.icon;
              return (
                <div
                  key={index}
                  className="card-modern p-6 text-center transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
                >
                  <span className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-full bg-blue-900/10">
                    <IconComp boxSize={10} className="text-blue-400 w-10 h-10" />
                  </span>
                  <h3 className="text-xl font-semibold mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="flex flex-col gap-6 text-center pt-8">
            <h2 className="text-3xl font-bold text-white">
              {t('about.whyChoose.heading', 'Why Choose LeadTap?')}
            </h2>
            <p className="text-gray-400 text-lg max-w-[800px] mx-auto leading-relaxed">
              {t('about.whyChoose.description', 'Our platform combines cutting-edge technology with user-friendly design to provide the most efficient and reliable Google Maps data extraction solution. Whether you\'re a small business looking for leads or an enterprise requiring bulk data extraction, LeadTap has the tools and features you need to succeed.')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About; 