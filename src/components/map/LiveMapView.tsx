import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

const driverIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function FlyTo({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lng) map.setView([lat, lng], map.getZoom());
  }, [lat, lng, map]);
  return null;
}

interface LiveMapViewProps {
  tripId: string;
  initialCenter?: { lat: number; lng: number };
  pickup?: { lat: number; lng: number } | null;
  destination?: { lat: number; lng: number } | null;
}

export default function LiveMapView({ tripId, initialCenter = { lat: 0, lng: 0 }, pickup = null, destination = null }: LiveMapViewProps) {
  const [driverPos, setDriverPos] = useState<{ lat: number; lng: number } | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/trips/${tripId}/`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'location_update' || data.type === 'location.update') {
          setDriverPos({ lat: data.lat, lng: data.lng });
        }
      } catch (e) {
        console.error('ws parse', e);
      }
    };
    ws.onopen = () => console.debug('ws open');
    ws.onclose = () => console.debug('ws closed');
    return () => { ws.close(); };
  }, [tripId]);

  const center = driverPos || initialCenter;

  return (
    <div style={{ height: 400, width: '100%' }}>
      <MapContainer center={[center.lat, center.lng]} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {driverPos && (
          <>
            <Marker position={[driverPos.lat, driverPos.lng]} icon={driverIcon}>
              <Popup>Driver</Popup>
            </Marker>
            <FlyTo lat={driverPos.lat} lng={driverPos.lng} />
          </>
        )}
        {pickup && (<Marker position={[pickup.lat, pickup.lng]}><Popup>Pickup</Popup></Marker>)}
        {destination && (<Marker position={[destination.lat, destination.lng]}><Popup>Destination</Popup></Marker>)}
      </MapContainer>
    </div>
  );
}
