import { useEffect, useRef } from 'react';

interface LogConsoleProps {
  logs: string[];
}

export default function LogConsole({ logs }: LogConsoleProps) {
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="glass-strong rounded-xl p-4 h-32 overflow-y-auto">
      <div className="font-mono text-xs space-y-1">
        {logs.length === 0 ? (
          <div className="text-gray-500 dark:text-gray-400">No logs yet...</div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="text-green-400 dark:text-green-300 mb-1">
              {log}
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}

