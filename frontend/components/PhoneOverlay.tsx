import React from 'react';

interface PhoneCoordinates {
  x: number;
  y: number;
  width: number;
  height: number;
  absolute_x?: number;
  absolute_y?: number;
  viewport_width?: number;
  viewport_height?: number;
  scroll_x?: number;
  scroll_y?: number;
}

interface PhoneOverlayProps {
  coordinates: PhoneCoordinates;
  phoneNumber: string;
  source: string;
  confidence: number;
  onClick?: () => void;
  containerWidth: number;
  containerHeight: number;
}

export default function PhoneOverlay({
  coordinates,
  phoneNumber,
  source,
  confidence,
  onClick,
  containerWidth,
  containerHeight,
}: PhoneOverlayProps) {
  // Calculate absolute pixel positions from normalized coordinates
  const x = coordinates.x * containerWidth;
  const y = coordinates.y * containerHeight;
  const width = coordinates.width * containerWidth;
  const height = coordinates.height * containerHeight;

  // Determine highlight color based on confidence
  const getColor = () => {
    if (confidence >= 80) return 'rgba(34, 197, 94, 0.3)'; // Green for high confidence
    if (confidence >= 60) return 'rgba(234, 179, 8, 0.3)'; // Yellow for medium confidence
    return 'rgba(239, 68, 68, 0.3)'; // Red for low confidence
  };

  const borderColor = getColor().replace('0.3', '0.8');

  return (
    <div
      className="absolute pointer-events-auto cursor-pointer transition-all duration-200 hover:opacity-100"
      style={{
        left: `${x}px`,
        top: `${y}px`,
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: getColor(),
        border: `2px solid ${borderColor}`,
        borderRadius: '4px',
        zIndex: 10,
      }}
      onClick={onClick}
      title={`${phoneNumber} (${source}, ${confidence}% confidence)`}
    >
      {/* Tooltip on hover */}
      <div className="absolute -top-8 left-0 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 hover:opacity-100 pointer-events-none whitespace-nowrap">
        {phoneNumber} ({confidence}%)
      </div>
    </div>
  );
}

