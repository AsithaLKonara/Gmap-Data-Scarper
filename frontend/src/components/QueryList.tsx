import React from 'react';

type QueryListProps = {
  queries: string[];
  onRemove: (q: string) => void;
};

const CloseIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="w-3 h-3"><line x1="6" y1="6" x2="14" y2="14" /><line x1="14" y1="6" x2="6" y2="14" /></svg>
);

const QueryList: React.FC<QueryListProps> = ({ queries, onRemove }) => (
  <ul className="space-y-2">
    {queries.map(q => (
      <li key={q} className="flex items-center justify-between bg-white p-2 rounded-md shadow-sm">
        <span>{q}</span>
        <button
          aria-label="Remove"
          type="button"
          onClick={() => onRemove(q)}
          className="inline-flex items-center justify-center rounded-full p-1 hover:bg-gray-100 focus:outline-none"
        >
          <CloseIcon />
        </button>
      </li>
    ))}
  </ul>
);

export default QueryList; 