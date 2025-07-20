import React from 'react';

export const Chart = ({ title = 'Chart', data = [] }) => (
  <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 16, minHeight: 200, background: '#fafafa' }}>
    <h3 style={{ marginBottom: 8 }}>{title}</h3>
    <div style={{ color: '#bbb' }}>
      [Chart Placeholder]
    </div>
    <pre style={{ fontSize: 10, color: '#ccc' }}>{JSON.stringify(data, null, 2)}</pre>
  </div>
);

export default Chart; 