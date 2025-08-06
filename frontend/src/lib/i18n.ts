import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      welcome: 'Welcome',
      pricing: 'Pricing',
      dashboard: {
        tabs: {
          dashboard: 'Dashboard',
          crm: 'CRM',
          analytics: 'Analytics'
        },
        stats: {
          queriesToday: {
            label: 'Queries Today',
            helpText: 'Daily limit used'
          },
          totalJobs: {
            label: 'Total Jobs',
            helpText: 'All time jobs created'
          },
          crmLeads: {
            label: 'CRM Leads',
            helpText: 'Leads in your CRM'
          },
          plan: {
            label: 'Current Plan'
          }
        },
        planStatus: {
          limitReached: {
            title: 'Daily Limit Reached',
            description: 'You have used all your daily queries. Upgrade to continue.',
            upgradeButton: 'Upgrade Now'
          }
        },
        apiKeyManagement: {
          title: 'API Key Management',
          description: 'Generate and manage your API keys for programmatic access.',
          newApiKey: {
            title: 'New API Key Generated',
            warning: 'Copy this key now. It will not be shown again.'
          },
          activeApiKey: {
            title: 'Active API Key',
            createdAt: 'Created',
            lastUsed: 'Last Used'
          },
          noApiKey: 'No API key generated yet.',
          generateApiKeyButton: 'Generate API Key',
          revokeApiKeyButton: 'Revoke API Key'
        },
        supportContact: {
          title: 'Support & Contact',
          contactSupportButton: 'Contact Support',
          availableOptions: 'Available support options:',
          priorityBadge: 'PRIORITY SUPPORT'
        },
        savedSearches: {
          title: 'Saved Searches',
          saveTemplateButton: 'Save Template',
          noSavedSearches: 'No saved searches yet.',
          editButton: 'Edit',
          deleteButton: 'Delete'
        },
        dashboardSection: {
          title: 'LeadTap Dashboard',
          description: 'Create and manage your Google Maps scraping jobs.'
        },
        createNewJob: {
          title: 'Create New Job',
          description: 'Enter your search queries below. One query per line.',
          placeholder: 'e.g., restaurants in New York\ncoffee shops in San Francisco\npizza places in Chicago',
          createJobButton: 'Create Job',
          dailyLimitReached: 'Daily limit reached ({limit} queries)'
        },
        yourJobs: {
          title: 'Your Jobs',
          noJobsCreated: 'No jobs created yet.',
          selectAll: 'Select All',
          unselectAll: 'Unselect All',
          exportCsvButton: 'Export CSV',
          exportJsonButton: 'Export JSON',
          deleteButton: 'Delete'
        },
        jobItem: {
          jobId: 'Job #{id}'
        },
        gmapIframe: {
          title: 'Google Maps Preview',
          noQueryMessage: 'Select a job to see the map preview'
        },
        searchResults: {
          title: 'Search Results',
          advancedFilters: 'Advanced Filters:',
          statusOptions: {
            completed: 'Completed',
            pending: 'Pending',
            failed: 'Failed'
          },
          companyPlaceholder: 'Filter by company',
          applyFiltersButton: 'Apply Filters',
          resetFiltersButton: 'Reset',
          noResults: 'No results found.',
          actions: 'Actions',
          addCrmButton: 'Add to CRM',
          exportFormats: {
            CSV: 'Export CSV',
            JSON: 'Export JSON',
            XLSX: 'Export Excel',
            PDF: 'Export PDF'
          }
        },
        upgradeModal: {
          title: 'Upgrade Your Plan',
          choosePlan: 'Choose a plan that fits your needs:',
          freePlan: {
            title: 'Free Plan',
            description: 'Basic scraping with limited queries',
            included: '5 queries per day'
          },
          proPlan: {
            title: 'Pro Plan',
            description: 'Advanced features and more queries',
            bestFor: 'Best for small businesses'
          },
          businessPlan: {
            title: 'Business Plan',
            description: 'Enterprise features and unlimited queries',
            for: 'For large teams and agencies'
          },
          cancelButton: 'Cancel',
          upgradeNowButton: 'Upgrade Now'
        },
        addLeadModal: {
          title: 'Add New Lead',
          nameLabel: 'Name',
          emailLabel: 'Email',
          phoneLabel: 'Phone',
          companyLabel: 'Company',
          websiteLabel: 'Website',
          notesLabel: 'Notes',
          addButton: 'Add Lead',
          cancelButton: 'Cancel'
        },
        notifications: {
          title: 'Notifications',
          noNotifications: 'No notifications yet.',
          markAllRead: 'Mark all as read'
        }
      }
    }
  },
  es: {
    translation: {
      welcome: 'Bienvenido',
      pricing: 'Precios',
      dashboard: {
        tabs: {
          dashboard: 'Panel',
          crm: 'CRM',
          analytics: 'Analíticas'
        },
        stats: {
          queriesToday: {
            label: 'Consultas Hoy',
            helpText: 'Límite diario usado'
          },
          totalJobs: {
            label: 'Trabajos Totales',
            helpText: 'Todos los trabajos creados'
          },
          crmLeads: {
            label: 'Leads CRM',
            helpText: 'Leads en tu CRM'
          },
          plan: {
            label: 'Plan Actual'
          }
        },
        planStatus: {
          limitReached: {
            title: 'Límite Diario Alcanzado',
            description: 'Has usado todas tus consultas diarias. Actualiza para continuar.',
            upgradeButton: 'Actualizar Ahora'
          }
        },
        apiKeyManagement: {
          title: 'Gestión de Claves API',
          description: 'Genera y gestiona tus claves API para acceso programático.',
          newApiKey: {
            title: 'Nueva Clave API Generada',
            warning: 'Copia esta clave ahora. No se mostrará de nuevo.'
          },
          activeApiKey: {
            title: 'Clave API Activa',
            createdAt: 'Creada',
            lastUsed: 'Último Uso'
          },
          noApiKey: 'Aún no se ha generado ninguna clave API.',
          generateApiKeyButton: 'Generar Clave API',
          revokeApiKeyButton: 'Revocar Clave API'
        },
        supportContact: {
          title: 'Soporte y Contacto',
          contactSupportButton: 'Contactar Soporte',
          availableOptions: 'Opciones de soporte disponibles:',
          priorityBadge: 'SOPORTE PRIORITARIO'
        },
        savedSearches: {
          title: 'Búsquedas Guardadas',
          saveTemplateButton: 'Guardar Plantilla',
          noSavedSearches: 'Aún no hay búsquedas guardadas.',
          editButton: 'Editar',
          deleteButton: 'Eliminar'
        },
        dashboardSection: {
          title: 'Panel LeadTap',
          description: 'Crea y gestiona tus trabajos de scraping de Google Maps.'
        },
        createNewJob: {
          title: 'Crear Nuevo Trabajo',
          description: 'Ingresa tus consultas de búsqueda a continuación. Una consulta por línea.',
          placeholder: 'ej., restaurantes en Nueva York\ncafeterías en San Francisco\npizzerías en Chicago',
          createJobButton: 'Crear Trabajo',
          dailyLimitReached: 'Límite diario alcanzado ({limit} consultas)'
        },
        yourJobs: {
          title: 'Tus Trabajos',
          noJobsCreated: 'Aún no se han creado trabajos.',
          selectAll: 'Seleccionar Todo',
          unselectAll: 'Deseleccionar Todo',
          exportCsvButton: 'Exportar CSV',
          exportJsonButton: 'Exportar JSON',
          deleteButton: 'Eliminar'
        },
        jobItem: {
          jobId: 'Trabajo #{id}'
        },
        gmapIframe: {
          title: 'Vista Previa de Google Maps',
          noQueryMessage: 'Selecciona un trabajo para ver la vista previa del mapa'
        },
        searchResults: {
          title: 'Resultados de Búsqueda',
          advancedFilters: 'Filtros Avanzados:',
          statusOptions: {
            completed: 'Completado',
            pending: 'Pendiente',
            failed: 'Fallido'
          },
          companyPlaceholder: 'Filtrar por empresa',
          applyFiltersButton: 'Aplicar Filtros',
          resetFiltersButton: 'Restablecer',
          noResults: 'No se encontraron resultados.',
          actions: 'Acciones',
          addCrmButton: 'Agregar al CRM',
          exportFormats: {
            CSV: 'Exportar CSV',
            JSON: 'Exportar JSON',
            XLSX: 'Exportar Excel',
            PDF: 'Exportar PDF'
          }
        },
        upgradeModal: {
          title: 'Actualiza Tu Plan',
          choosePlan: 'Elige un plan que se adapte a tus necesidades:',
          freePlan: {
            title: 'Plan Gratuito',
            description: 'Scraping básico con consultas limitadas',
            included: '5 consultas por día'
          },
          proPlan: {
            title: 'Plan Pro',
            description: 'Funciones avanzadas y más consultas',
            bestFor: 'Ideal para pequeñas empresas'
          },
          businessPlan: {
            title: 'Plan Empresarial',
            description: 'Funciones empresariales y consultas ilimitadas',
            for: 'Para equipos grandes y agencias'
          },
          cancelButton: 'Cancelar',
          upgradeNowButton: 'Actualizar Ahora'
        },
        addLeadModal: {
          title: 'Agregar Nuevo Lead',
          nameLabel: 'Nombre',
          emailLabel: 'Email',
          phoneLabel: 'Teléfono',
          companyLabel: 'Empresa',
          websiteLabel: 'Sitio Web',
          notesLabel: 'Notas',
          addButton: 'Agregar Lead',
          cancelButton: 'Cancelar'
        },
        notifications: {
          title: 'Notificaciones',
          noNotifications: 'Aún no hay notificaciones.',
          markAllRead: 'Marcar todo como leído'
        }
      },
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
