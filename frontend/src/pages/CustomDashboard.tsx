import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';

const defaultWidgets = [
  { id: 'stats', label: 'Stats', content: <div>Stats Widget</div> },
  { id: 'leads', label: 'Leads', content: <div>Leads Widget</div> },
  { id: 'analytics', label: 'Analytics', content: <div>Analytics Widget</div> },
  { id: 'tasks', label: 'Tasks', content: <div>Tasks Widget</div> },
];

export const CustomDashboard: React.FC = () => {
  const [widgets, setWidgets] = useState(() => {
    const saved = localStorage.getItem('dashboard_widgets');
    return saved ? JSON.parse(saved) : defaultWidgets;
  });
  const [draggedId, setDraggedId] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('dashboard_widgets', JSON.stringify(widgets));
  }, [widgets]);

  const onDragStart = (id: string) => setDraggedId(id);
  const onDragOver = (id: string) => {
    if (draggedId && draggedId !== id) {
      const fromIdx = widgets.findIndex(w => w.id === draggedId);
      const toIdx = widgets.findIndex(w => w.id === id);
      const newWidgets = [...widgets];
      const [moved] = newWidgets.splice(fromIdx, 1);
      newWidgets.splice(toIdx, 0, moved);
      setWidgets(newWidgets);
    }
  };
  const onDragEnd = () => setDraggedId(null);

  const toggleWidget = (id: string) => {
    setWidgets(widgets => widgets.map(w => w.id === id ? { ...w, hidden: !w.hidden } : w));
  };

  return (
    <div className="p-6">
      <div className="mb-4 flex gap-2">
        {widgets.map(w => (
          <Button key={w.id} size="sm" variant={w.hidden ? 'outline' : 'default'} onClick={() => toggleWidget(w.id)}>
            {w.hidden ? `Show ${w.label}` : `Hide ${w.label}`}
          </Button>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {widgets.filter(w => !w.hidden).map(w => (
          <Card
            key={w.id}
            draggable
            onDragStart={() => onDragStart(w.id)}
            onDragOver={() => onDragOver(w.id)}
            onDragEnd={onDragEnd}
            className={draggedId === w.id ? 'opacity-50' : ''}
          >
            <CardHeader>{w.label}</CardHeader>
            <CardContent>{w.content}</CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}; 