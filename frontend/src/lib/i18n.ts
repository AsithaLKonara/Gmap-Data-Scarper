import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      welcome: 'Welcome',
      pricing: 'Pricing',
      dashboard: 'Dashboard',
      crm: 'CRM',
      notifications: 'Notifications',
      login: 'Login',
      logout: 'Logout',
      // Add more keys as needed
    },
  },
  es: {
    translation: {
      welcome: 'Bienvenido',
      pricing: 'Precios',
      dashboard: 'Panel',
      crm: 'CRM',
      notifications: 'Notificaciones',
      login: 'Iniciar sesión',
      logout: 'Cerrar sesión',
      // Add more keys as needed
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

export default i18n; 