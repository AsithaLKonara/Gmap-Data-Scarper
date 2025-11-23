"""Location-aware lead segmentation using reverse geocoding."""
from __future__ import annotations

import re
import time
import math
from typing import Dict, Optional, Tuple, List
from urllib.parse import quote

import requests


class GeolocationExtractor:
    """
    Extracts location data from addresses using reverse geocoding.
    
    Uses OpenStreetMap Nominatim API (no API key required).
    """
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize geolocation extractor.
        
        Args:
            delay_seconds: Delay between API requests to respect rate limits
        """
        self.delay_seconds = delay_seconds
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.last_request_time = 0.0
    
    def extract_location(self, address: str) -> Dict[str, str]:
        """
        Extract location components from an address string.
        
        Args:
            address: Full address string
            
        Returns:
            Dictionary with city, region, country, postal_code
        """
        if not address or address == "N/A":
            return {
                "city": "N/A",
                "region": "N/A",
                "country": "N/A",
                "postal_code": "N/A"
            }
        
        # First try simple parsing (faster, no API call)
        parsed = self._parse_address_simple(address)
        if parsed["city"] != "N/A":
            return parsed
        
        # If simple parsing fails, try reverse geocoding
        try:
            return self._reverse_geocode(address)
        except Exception as e:
            print(f"[GEOLOCATION] Error geocoding address: {e}")
            return parsed
    
    def _parse_address_simple(self, address: str) -> Dict[str, str]:
        """
        Simple address parsing without API calls.
        
        Tries to extract city, region, country, postal_code from common formats.
        """
        result = {
            "city": "N/A",
            "region": "N/A",
            "country": "N/A",
            "postal_code": "N/A"
        }
        
        # Extract postal code (common formats)
        postal_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)  # US format
        if not postal_match:
            postal_match = re.search(r'\b[A-Z0-9]{3,8}\b', address)  # International
        if postal_match:
            result["postal_code"] = postal_match.group(0)
        
        # Common address patterns
        # Format: "Street, City, State ZIP" or "Street, City, Country"
        parts = [p.strip() for p in address.split(",")]
        
        if len(parts) >= 2:
            # Last part might be country or state+zip
            last_part = parts[-1]
            
            # Check if it's a US state abbreviation
            us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
            
            if any(state in last_part.upper() for state in us_states):
                result["region"] = last_part.split()[0] if " " in last_part else last_part
                if len(parts) >= 3:
                    result["city"] = parts[-2]
            else:
                # Might be country
                result["country"] = last_part
                if len(parts) >= 3:
                    result["city"] = parts[-2]
                if len(parts) >= 4:
                    result["region"] = parts[-3]
        
        if len(parts) >= 1 and result["city"] == "N/A":
            # Try to extract city from first meaningful part
            for part in parts:
                if part and not part[0].isdigit():  # Not a street number
                    result["city"] = part
                    break
        
        return result
    
    def _reverse_geocode(self, address: str) -> Dict[str, str]:
        """
        Use Nominatim API for reverse geocoding.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Dictionary with location components
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay_seconds:
            time.sleep(self.delay_seconds - time_since_last)
        
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "LeadScraper/1.0"  # Required by Nominatim
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return self._parse_address_simple(address)
            
            result_data = data[0].get("address", {})
            
            result = {
                "city": result_data.get("city") or 
                       result_data.get("town") or 
                       result_data.get("village") or 
                       result_data.get("municipality") or "N/A",
                "region": result_data.get("state") or 
                         result_data.get("region") or 
                         result_data.get("province") or "N/A",
                "country": result_data.get("country") or "N/A",
                "postal_code": result_data.get("postcode") or "N/A"
            }
            
            self.last_request_time = time.time()
            return result
            
        except Exception as e:
            print(f"[GEOLOCATION] API error: {e}")
            return self._parse_address_simple(address)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates (latitude, longitude) for a location string.
        
        Args:
            location: Location string (city, address, etc.)
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Use reverse geocoding to get coordinates
            parsed = self.extract_location(location)
            if parsed["city"] == "N/A" and parsed["country"] == "N/A":
                return None
            
            # Build search query
            search_query = location
            if parsed["city"] != "N/A":
                search_query = f"{parsed['city']}, {parsed['country']}"
            
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_request_time < self.delay_seconds:
                time.sleep(self.delay_seconds - (current_time - self.last_request_time))
            
            params = {
                "q": search_query,
                "format": "json",
                "limit": 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result.get("lat", 0))
                    lon = float(result.get("lon", 0))
                    if lat != 0 or lon != 0:
                        return (lat, lon)
        except Exception:
            pass
        
        return None
    
    def filter_by_location(self, results: list, location: str, radius_km: Optional[float] = None) -> list:
        """
        Filter results by location (simple city/region matching or radius-based).
        
        Args:
            results: List of ScrapeResult dictionaries
            location: Location string to match (city, region, or country)
            radius_km: Optional radius in kilometers for coordinate-based filtering
            
        Returns:
            Filtered list of results
        """
        if not location:
            return results
        
        # If radius is specified, use coordinate-based filtering
        if radius_km is not None and radius_km > 0:
            center_coords = self._get_coordinates(location)
            if center_coords:
                center_lat, center_lon = center_coords
                filtered = []
                
                for result in results:
                    # Try to get coordinates from result
                    result_lat = result.get("latitude") or result.get("lat")
                    result_lon = result.get("longitude") or result.get("lon")
                    
                    if result_lat is not None and result_lon is not None:
                        try:
                            result_lat = float(result_lat)
                            result_lon = float(result_lon)
                            distance = self._haversine_distance(
                                center_lat, center_lon, result_lat, result_lon
                            )
                            if distance <= radius_km:
                                filtered.append(result)
                        except (ValueError, TypeError):
                            # If coordinates are invalid, fall back to text matching
                            location_lower = location.lower()
                            city = result.get("city", "").lower()
                            region = result.get("region", "").lower()
                            country = result.get("country", "").lower()
                            address = result.get("Address", "").lower()
                            
                            if (location_lower in city or 
                                location_lower in region or 
                                location_lower in country or
                                location_lower in address):
                                filtered.append(result)
                    else:
                        # No coordinates, fall back to text matching
                        location_lower = location.lower()
                        city = result.get("city", "").lower()
                        region = result.get("region", "").lower()
                        country = result.get("country", "").lower()
                        address = result.get("Address", "").lower()
                        
                        if (location_lower in city or 
                            location_lower in region or 
                            location_lower in country or
                            location_lower in address):
                            filtered.append(result)
                
                return filtered
        
        # Simple text-based filtering (original implementation)
        location_lower = location.lower()
        filtered = []
        
        for result in results:
            city = result.get("city", "").lower()
            region = result.get("region", "").lower()
            country = result.get("country", "").lower()
            address = result.get("Address", "").lower()
            
            if (location_lower in city or 
                location_lower in region or 
                location_lower in country or
                location_lower in address):
                filtered.append(result)
        
        return filtered

