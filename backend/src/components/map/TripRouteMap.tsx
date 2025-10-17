import React from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import type { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';

type LineString = {
  type: 'LineString';
  coordinates: Array<[number, number]>; // [lng, lat]
};

type Props = {
  geometry?: LineString | null;
  origin?: { lat: number; lng: number } | null;
  destination?: { lat: number; lng: number } | null;
  steps?: Array<{ instruction: string; distance_m?: number; duration_s?: number }> | null;
};

export const TripRouteMap: React.FC<Props> = ({ geometry, origin, destination, steps }) => {
  const defaultCenter = origin || (geometry && { lat: geometry.coordinates[0][1], lng: geometry.coordinates[0][0] }) || { lat: 39.5, lng: -98.35 };

  const latlngs = geometry ? geometry.coordinates.map((c) => [c[1], c[0]]) : [];

  return (
    <div className="rounded-lg overflow-hidden border border-slate-200">
      <MapContainer center={[defaultCenter.lat, defaultCenter.lng]} zoom={5} style={{ height: 360, width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {latlngs.length > 0 && (
          // positions expects an array of LatLng tuples; cast to LatLngExpression[]
          <Polyline positions={latlngs as unknown as LatLngExpression[]} color="blue" />
        )}
        {origin && <Marker position={[origin.lat, origin.lng]}><Popup>Origin</Popup></Marker>}
        {destination && <Marker position={[destination.lat, destination.lng]}><Popup>Destination</Popup></Marker>}
      </MapContainer>

      {steps && (
        <div className="p-4">
          <h3 className="font-semibold">Steps</h3>
          <ol className="list-decimal list-inside text-sm mt-2">
            {steps.map((s, i) => (
              <li key={i} className="mb-1">
                {s.instruction} {s.distance_m ? ` — ${Math.round(s.distance_m)} m` : ''}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

export default TripRouteMap;
