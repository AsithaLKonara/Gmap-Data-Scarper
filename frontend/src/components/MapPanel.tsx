import React from 'react';
import { Box, Text } from '@chakra-ui/react';
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
    <Box p={4}>
      <Text fontSize="lg" mb={4}>Map View</Text>
      <LoadScript googleMapsApiKey="YOUR_GOOGLE_MAPS_API_KEY">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={10}
        >
          <Marker position={center} />
        </GoogleMap>
      </LoadScript>
    </Box>
  );
};

export default MapPanel; 