import React from 'react';

type QueryInputProps = {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onAdd: () => void;
};

const QueryInput: React.FC<QueryInputProps> = ({ value, onChange, onAdd }) => (
  <div className="flex items-center space-x-2">
    <input
      type="text"
      placeholder="Enter search query"
      value={value}
      onChange={onChange}
      onKeyDown={e => e.key === 'Enter' && onAdd()}
      className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    />
    <button
      type="button"
      onClick={onAdd}
      className="inline-flex items-center justify-center whitespace-nowrap rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    >
      Add
    </button>
  </div>
);

export default QueryInput; 