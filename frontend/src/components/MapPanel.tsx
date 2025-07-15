import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const MapPanel = () => {
  const mapContainerStyle = {
    width: '100%',
    height: '400px'
  };

  const center = {
    lat: 6.9271, // Colombo, Sri Lanka
    lng: 79.8612
  };

  return (
    <div className="p-4">
      <span className="text-lg font-semibold mb-4 block">Map View</span>
      <LoadScript googleMapsApiKey="YOUR_GOOGLE_MAPS_API_KEY">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={10}
        >
          <Marker position={center} />
        </GoogleMap>
      </LoadScript>
    </div>
  );
};

export default MapPanel; 