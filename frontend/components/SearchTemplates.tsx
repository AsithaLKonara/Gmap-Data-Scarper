import { useState, useEffect } from 'react';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';

interface Template {
  name: string;
  description: string;
  lead_objective?: string;
}

interface SearchTemplatesProps {
  onSelectTemplate: (template: any) => void;
}

export default function SearchTemplates({ onSelectTemplate }: SearchTemplatesProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [templateDetails, setTemplateDetails] = useState<any>(null);
  const [variables, setVariables] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    if (selectedTemplate) {
      loadTemplateDetails(selectedTemplate);
    }
  }, [selectedTemplate]);

  const loadTemplates = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/templates/`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const loadTemplateDetails = async (templateName: string) => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/templates/${encodeURIComponent(templateName)}`);
      if (response.ok) {
        const data = await response.json();
        setTemplateDetails(data);
        
        // Extract variables from template
        const vars: Record<string, string> = {};
        if (data.queries) {
          data.queries.forEach((q: string) => {
            const matches = q.match(/\{(\w+)\}/g);
            if (matches) {
              matches.forEach(match => {
                const varName = match.replace(/[{}]/g, '');
                if (!vars[varName]) {
                  vars[varName] = '';
                }
              });
            }
          });
        }
        setVariables(vars);
      }
    } catch (err) {
      console.error('Failed to load template details:', err);
    }
  };

  const handleApplyTemplate = async () => {
    if (!selectedTemplate) return;

    setIsLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/templates/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_name: selectedTemplate,
          variables: variables,
        }),
      });

      if (response.ok) {
        const applied = await response.json();
        onSelectTemplate(applied);
      }
    } catch (err) {
      console.error('Failed to apply template:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <GlassCard>
      <h2 className="font-semibold mb-4 text-lg text-gradient-primary">Search Templates</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Choose a pre-configured template to quickly set up your search.
      </p>

      <div className="space-y-3">
        <select
          value={selectedTemplate}
          onChange={(e) => setSelectedTemplate(e.target.value)}
          className="input-glass w-full text-sm"
        >
          <option value="">Select a template...</option>
          {templates.map((template) => (
            <option key={template.name} value={template.name}>
              {template.name} - {template.description}
            </option>
          ))}
        </select>

        {templateDetails && (
          <div className="mt-4 space-y-3">
            <div className="p-3 glass-subtle rounded-lg">
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                {templateDetails.description}
              </p>
              
              {Object.keys(variables).length > 0 && (
                <div className="space-y-2">
                  <strong className="text-xs">Template Variables:</strong>
                  {Object.keys(variables).map((varName) => (
                    <GlassInput
                      key={varName}
                      type="text"
                      value={variables[varName]}
                      onChange={(e) => {
                        setVariables({
                          ...variables,
                          [varName]: e.target.value,
                        });
                      }}
                      placeholder={`Enter ${varName.replace('_', ' ')}`}
                      className="w-full text-xs"
                    />
                  ))}
                </div>
              )}

              <div className="mt-3">
                <strong className="text-xs">Preview Queries:</strong>
                <ul className="list-disc list-inside text-xs mt-1 text-gray-600 dark:text-gray-400">
                  {templateDetails.queries?.slice(0, 3).map((q: string, idx: number) => {
                    let preview = q;
                    Object.keys(variables).forEach(varName => {
                      preview = preview.replace(`{${varName}}`, variables[varName] || `[${varName}]`);
                    });
                    return <li key={idx}>{preview}</li>;
                  })}
                </ul>
              </div>

              <GlassButton
                onClick={handleApplyTemplate}
                disabled={isLoading || !selectedTemplate}
                variant="primary"
                gradient
                className="w-full mt-3"
                size="sm"
              >
                {isLoading ? 'Applying...' : 'Apply Template'}
              </GlassButton>
            </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}

