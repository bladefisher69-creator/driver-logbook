import React, { useState } from 'react';
import { X, AlertCircle } from 'lucide-react';
import { apiClient } from '../../api/client';
import { Trip } from '../../types';
import TripRouteMap from '../map/TripRouteMap';
import MapPicker from '../map/MapPicker';
import AddressSearch from '../map/AddressSearch';
import useGeolocationTracker from '../map/GeolocationTracker';
import LiveMapView from '../map/LiveMapView';

interface TripFormProps {
  trip: Trip | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const TripForm: React.FC<TripFormProps> = ({ trip, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    vehicle_id: trip?.vehicle_id || '',
    origin: trip?.origin || '',
    destination: trip?.destination || '',
    distance: trip?.distance || '',
    start_time: trip?.start_time ? new Date(trip.start_time).toISOString().slice(0, 16) : '',
    pickup_time: trip?.pickup_time || 1,
    dropoff_time: trip?.dropoff_time || 1,
    notes: trip?.notes || '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  type RouteStep = { instruction: string; distance_m?: number; duration_s?: number };
  type LineString = { type: 'LineString'; coordinates: Array<[number, number]> };
  type RouteResponse = {
    geometry?: LineString;
    steps?: RouteStep[];
    distance_m?: number;
    duration_s?: number;
    provider?: string;
    error?: string;
  };

  const [routeData, setRouteData] = useState<RouteResponse | { error: string } | null>(null);
  const [showMap, setShowMap] = useState(false);
  const [mapMode, setMapMode] = useState<'origin' | 'destination' | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      // Normalize payload: convert numeric-like strings to numbers and
      // ensure start_time is an ISO datetime string (backend expects full ISO format).
      const payload = {
        ...formData,
        distance: String(formData.distance).trim() === '' ? null : Number(formData.distance),
        pickup_time: String(formData.pickup_time).trim() === '' ? null : Number(formData.pickup_time),
        dropoff_time: String(formData.dropoff_time).trim() === '' ? null : Number(formData.dropoff_time),
        start_time: formData.start_time ? new Date(formData.start_time).toISOString() : null,
      };

      await apiClient.post('/trips/', payload);
      onSuccess();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : (typeof err === 'string' ? err : JSON.stringify(err));
      setError(message || 'Failed to create trip');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleShowRoute = async () => {
    setRouteData(null);
    setShowMap(true);
    try {
      // For M1: attempt to interpret origin/destination as lat,lng if provided as comma-separated; otherwise this will rely on backend ORS which needs coords.
      const parseLatLng = (s: string) => {
        const parts = s.split(',').map(p => p.trim());
        if (parts.length === 2 && !isNaN(Number(parts[0])) && !isNaN(Number(parts[1]))) {
          return { lat: Number(parts[0]), lng: Number(parts[1]) };
        }
        return null;
      };

      const originCoord = parseLatLng(formData.origin as string);
      const destCoord = parseLatLng(formData.destination as string);

      if (!originCoord || !destCoord) {
        // Fallback: show message in map area; backend ORS needs coords. For now we abort and show error.
        setRouteData({ error: 'Please enter origin and destination as "lat,lng" for route preview in this development build.' });
        return;
      }

  const resp = await apiClient.post<RouteResponse>('/route/', { origin: originCoord, destination: destCoord });
  // apiClient.request returns parsed JSON directly
  setRouteData(resp as RouteResponse);
    } catch (err: unknown) {
      // Normalize error display safely
      const message = err instanceof Error ? err.message : (typeof err === 'string' ? err : JSON.stringify(err));
      setRouteData({ error: message });
    }
  };

  // Geolocation tracking (only active when we have a trip id to post to)
  const tracker = useGeolocationTracker({ tripId: trip?.id ? String(trip.id) : '' });
  const [isTracking, setIsTracking] = useState(false);

  const openMapPicker = (mode: 'origin' | 'destination') => {
    setMapMode(mode);
    setShowMap(true);
  };

  const handlePick = async (p: { lat: number; lng: number }) => {
    // Call reverse geocode to get place name
    try {
      const rev = await apiClient.get<{ place_name?: string; address?: string }>(`/search/reverse/?lat=${p.lat}&lng=${p.lng}`, { requiresAuth: false });
      const name = rev.place_name || `${p.lat.toFixed(5)},${p.lng.toFixed(5)}`;
      if (mapMode === 'origin') {
        setFormData({ ...formData, origin: name });
        if (trip) {
          await apiClient.patch(`/trips/${trip.id}/pickup/`, { name, address: rev.address || name, lat: p.lat, lng: p.lng });
        }
      } else if (mapMode === 'destination') {
        setFormData({ ...formData, destination: name });
        if (trip) {
          await apiClient.patch(`/trips/${trip.id}/destination/`, { name, address: rev.address || name, lat: p.lat, lng: p.lng });
        }
      }
      setShowMap(false);
      setMapMode(null);
    } catch {
      // ignore for now
      setShowMap(false);
      setMapMode(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Start New Trip</h1>
          <p className="text-slate-600 mt-1">Log a new trip to your logbook</p>
        </div>
        <button
          onClick={onClose}
          aria-label="Close trip form"
          title="Close"
          className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="vehicle_id" className="block text-sm font-medium text-slate-700 mb-2">
                Vehicle ID *
              </label>
              <input
                id="vehicle_id"
                name="vehicle_id"
                type="text"
                value={formData.vehicle_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="TRK123"
              />
            </div>

            <div>
              <label htmlFor="distance" className="block text-sm font-medium text-slate-700 mb-2">
                Distance (miles) *
              </label>
              <input
                id="distance"
                name="distance"
                type="number"
                step="0.01"
                value={formData.distance}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="250"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="origin" className="block text-sm font-medium text-slate-700 mb-2">
                Origin *
              </label>
              <input
                id="origin"
                name="origin"
                type="text"
                value={formData.origin}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="New York, NY"
              />
              <div className="mt-2">
                <AddressSearch onSelect={async (s) => {
                  setFormData({ ...formData, origin: s.place_name });
                  if (trip) {
                    await apiClient.patch(`/trips/${trip.id}/pickup/`, { name: s.place_name, address: s.address || s.place_name, lat: s.lat, lng: s.lng });
                  }
                }} placeholder="Search origin..." />
              </div>
              <button type="button" onClick={() => openMapPicker('origin')} className="mt-2 text-sm text-blue-600">Pick on map</button>
            </div>

            <div>
              <label htmlFor="destination" className="block text-sm font-medium text-slate-700 mb-2">
                Destination *
              </label>
              <input
                id="destination"
                name="destination"
                type="text"
                value={formData.destination}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Boston, MA"
              />
              <div className="mt-2">
                <AddressSearch onSelect={async (s) => {
                  setFormData({ ...formData, destination: s.place_name });
                  if (trip) {
                    await apiClient.patch(`/trips/${trip.id}/destination/`, { name: s.place_name, address: s.address || s.place_name, lat: s.lat, lng: s.lng });
                  }
                }} placeholder="Search destination..." />
              </div>
              <button type="button" onClick={() => openMapPicker('destination')} className="mt-2 text-sm text-blue-600">Pick on map</button>
            </div>
          </div>

          <div>
            <label htmlFor="start_time" className="block text-sm font-medium text-slate-700 mb-2">
              Start Time *
            </label>
            <input
              id="start_time"
              name="start_time"
              type="datetime-local"
              value={formData.start_time}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="pickup_time" className="block text-sm font-medium text-slate-700 mb-2">
                Pickup Time (hours)
              </label>
              <input
                id="pickup_time"
                name="pickup_time"
                type="number"
                step="0.01"
                value={formData.pickup_time}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-slate-500 mt-1">Default: 1 hour</p>
            </div>

            <div>
              <label htmlFor="dropoff_time" className="block text-sm font-medium text-slate-700 mb-2">
                Drop-off Time (hours)
              </label>
              <input
                id="dropoff_time"
                name="dropoff_time"
                type="number"
                step="0.01"
                value={formData.dropoff_time}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-slate-500 mt-1">Default: 1 hour</p>
            </div>
          </div>

          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-slate-700 mb-2">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Add any additional notes about this trip..."
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleShowRoute}
              className="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              Show Route
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Starting Trip...' : 'Start Trip'}
            </button>
          </div>
        </form>
      </div>
      {trip && (
        <div className="mt-4 flex items-center space-x-3">
          {!isTracking ? (
            <button onClick={() => { try { tracker.start(); setIsTracking(true); } catch(e) { console.error(e); } }} className="px-4 py-2 bg-green-600 text-white rounded">Start Tracking</button>
          ) : (
            <button onClick={() => { tracker.stop(); setIsTracking(false); }} className="px-4 py-2 bg-red-600 text-white rounded">Stop Tracking</button>
          )}
          <span className="text-sm text-slate-600">Live tracking posts to server and appears on the live map below.</span>
        </div>
      )}
      {showMap && (
        <div className="mt-4">
              {routeData?.error ? (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">{JSON.stringify(routeData.error)}</div>
              ) : (
                // Only render TripRouteMap when we have a geometry field
                routeData && 'geometry' in routeData && routeData.geometry ? (
                  <TripRouteMap
                    geometry={routeData.geometry}
                    origin={{ lat: routeData.geometry.coordinates[0][1], lng: routeData.geometry.coordinates[0][0] }}
                    destination={{ lat: routeData.geometry.coordinates.slice(-1)[0][1], lng: routeData.geometry.coordinates.slice(-1)[0][0] }}
                    steps={routeData.steps}
                  />
                ) : (
                  <div className="p-4">No route data available for preview.</div>
                )
              )}
        </div>
      )}

      {/* Live Map View for active trip */}
      {trip && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Live Map</h3>
          <LiveMapView
            tripId={String(trip.id)}
            initialCenter={trip.pickup_lat && trip.pickup_lng ? { lat: trip.pickup_lat, lng: trip.pickup_lng } : { lat: 0, lng: 0 }}
            pickup={trip.pickup_lat && trip.pickup_lng ? { lat: trip.pickup_lat, lng: trip.pickup_lng } : null}
            destination={trip.destination_lat && trip.destination_lng ? { lat: trip.destination_lat, lng: trip.destination_lng } : null}
          />
        </div>
      )}

      {/* MapPicker modal */}
      {showMap && mapMode && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg w-11/12 md:w-3/4 p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Pick {mapMode === 'origin' ? 'Origin' : 'Destination'} on map</h3>
              <button onClick={() => { setShowMap(false); setMapMode(null); }} className="text-slate-600">Close</button>
            </div>
            <MapPicker onPick={handlePick} />
          </div>
        </div>
      )}
    </div>
  );
};
