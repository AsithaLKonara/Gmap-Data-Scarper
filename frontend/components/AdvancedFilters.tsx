import React, { useState } from 'react';
import GlassCard from './ui/GlassCard';
import GlassButton from './ui/GlassButton';
import GlassInput from './ui/GlassInput';
import GlassModal from './ui/GlassModal';

interface FilterPreset {
  name: string;
  filters: FilterValues;
}

interface FilterValues {
  platforms: string[];
  dateRange: { start: string; end: string } | null;
  hasPhone: boolean | null;
  fieldOfStudy: string;
  location: string;
  businessType: string[];
}

interface AdvancedFiltersProps {
  onFiltersChange: (filters: FilterValues) => void;
  availablePlatforms: string[];
  initialFilters?: FilterValues;
}

export default function AdvancedFilters({
  onFiltersChange,
  availablePlatforms,
  initialFilters,
}: AdvancedFiltersProps) {
  const [filters, setFilters] = useState<FilterValues>(
    initialFilters || {
      platforms: [],
      dateRange: null,
      hasPhone: null,
      fieldOfStudy: '',
      location: '',
      businessType: [],
    }
  );

  const [presets, setPresets] = useState<FilterPreset[]>([]);
  const [showPresetModal, setShowPresetModal] = useState(false);
  const [presetName, setPresetName] = useState('');

  const updateFilter = (key: keyof FilterValues, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const savePreset = () => {
    if (!presetName.trim()) return;

    const newPreset: FilterPreset = {
      name: presetName,
      filters: { ...filters },
    };

    setPresets([...presets, newPreset]);
    setPresetName('');
    setShowPresetModal(false);
  };

  const loadPreset = (preset: FilterPreset) => {
    setFilters(preset.filters);
    onFiltersChange(preset.filters);
  };

  const clearFilters = () => {
    const cleared: FilterValues = {
      platforms: [],
      dateRange: null,
      hasPhone: null,
      fieldOfStudy: '',
      location: '',
      businessType: [],
    };
    setFilters(cleared);
    onFiltersChange(cleared);
  };

  return (
    <GlassCard>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gradient-primary">Advanced Filters</h2>
        <div className="flex gap-2">
          <GlassButton
            size="sm"
            variant="secondary"
            onClick={() => setShowPresetModal(true)}
          >
            Save Preset
          </GlassButton>
          <GlassButton size="sm" variant="secondary" onClick={clearFilters}>
            Clear All
          </GlassButton>
        </div>
      </div>

      <div className="space-y-4">
        {/* Platform Multi-Select */}
        <div>
          <label className="block text-sm font-medium mb-2">Platforms</label>
          <div className="space-y-2">
            {availablePlatforms.map((platform) => (
              <label
                key={platform}
                className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all"
              >
                <input
                  type="checkbox"
                  checked={filters.platforms.includes(platform)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      updateFilter('platforms', [...filters.platforms, platform]);
                    } else {
                      updateFilter(
                        'platforms',
                        filters.platforms.filter((p) => p !== platform)
                      );
                    }
                  }}
                  className="w-4 h-4 rounded accent-primary"
                />
                <span className="capitalize">{platform.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium mb-2">Date Range</label>
          <div className="grid grid-cols-2 gap-2">
            <GlassInput
              type="date"
              value={filters.dateRange?.start || ''}
              onChange={(e) =>
                updateFilter('dateRange', {
                  start: e.target.value,
                  end: filters.dateRange?.end || '',
                })
              }
              placeholder="Start Date"
            />
            <GlassInput
              type="date"
              value={filters.dateRange?.end || ''}
              onChange={(e) =>
                updateFilter('dateRange', {
                  start: filters.dateRange?.start || '',
                  end: e.target.value,
                })
              }
              placeholder="End Date"
            />
          </div>
        </div>

        {/* Phone Filter */}
        <div>
          <label className="block text-sm font-medium mb-2">Phone Number</label>
          <div className="space-y-2">
            <label className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
              <input
                type="radio"
                name="phone"
                checked={filters.hasPhone === null}
                onChange={() => updateFilter('hasPhone', null)}
                className="w-4 h-4 accent-primary"
              />
              <span>All</span>
            </label>
            <label className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
              <input
                type="radio"
                name="phone"
                checked={filters.hasPhone === true}
                onChange={() => updateFilter('hasPhone', true)}
                className="w-4 h-4 accent-primary"
              />
              <span>With Phone</span>
            </label>
            <label className="flex items-center gap-3 p-2 glass-subtle rounded-lg hover:glass cursor-pointer transition-all">
              <input
                type="radio"
                name="phone"
                checked={filters.hasPhone === false}
                onChange={() => updateFilter('hasPhone', false)}
                className="w-4 h-4 accent-primary"
              />
              <span>Without Phone</span>
            </label>
          </div>
        </div>

        {/* Field of Study */}
        <GlassInput
          label="Field of Study"
          value={filters.fieldOfStudy}
          onChange={(e) => updateFilter('fieldOfStudy', e.target.value)}
          placeholder="e.g., ICT, Computer Science"
        />

        {/* Location */}
        <GlassInput
          label="Location"
          value={filters.location}
          onChange={(e) => updateFilter('location', e.target.value)}
          placeholder="e.g., Kandy, Toronto"
        />

        {/* Presets */}
        {presets.length > 0 && (
          <div>
            <label className="block text-sm font-medium mb-2">Saved Presets</label>
            <div className="space-y-2">
              {presets.map((preset, idx) => (
                <GlassButton
                  key={idx}
                  size="sm"
                  variant="secondary"
                  onClick={() => loadPreset(preset)}
                  className="w-full justify-start"
                >
                  {preset.name}
                </GlassButton>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Preset Save Modal */}
      <GlassModal
        isOpen={showPresetModal}
        onClose={() => {
          setShowPresetModal(false);
          setPresetName('');
        }}
        title="Save Filter Preset"
      >
        <div className="space-y-4">
          <GlassInput
            label="Preset Name"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="My Filter Preset"
          />
          <div className="flex gap-2 justify-end">
            <GlassButton
              variant="secondary"
              onClick={() => {
                setShowPresetModal(false);
                setPresetName('');
              }}
            >
              Cancel
            </GlassButton>
            <GlassButton variant="primary" gradient onClick={savePreset}>
              Save
            </GlassButton>
          </div>
        </div>
      </GlassModal>
    </GlassCard>
  );
}

