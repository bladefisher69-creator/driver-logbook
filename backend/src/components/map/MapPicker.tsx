import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

interface MapPickerProps {
  center?: { lat: number; lng: number };
  onPick: (p: { lat: number; lng: number }) => void;
}

const MapPicker: React.FC<MapPickerProps> = ({ center = { lat: 39.5, lng: -98.35 }, onPick }) => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const leafletMap = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    leafletMap.current = L.map(mapRef.current).setView([center.lat, center.lng], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(leafletMap.current);

    leafletMap.current.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;
      if (markerRef.current) markerRef.current.setLatLng([lat, lng]);
      else markerRef.current = L.marker([lat, lng]).addTo(leafletMap.current!);
      onPick({ lat, lng });
    });

    return () => {
      leafletMap.current?.remove();
      leafletMap.current = null;
    };
  }, [center.lat, center.lng, onPick]);

  return <div ref={mapRef} style={{ width: '100%', height: 400 }} />;
};

export default MapPicker;
