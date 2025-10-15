import { useEffect, useRef } from 'react';
import { apiClient } from '../../api/client';

interface TrackerOptions {
  tripId: string;
  token?: string;
  intervalMs?: number;
}

export default function useGeolocationTracker({ tripId, intervalMs = 1000 }: TrackerOptions) {
  const watchIdRef = useRef<number | null>(null);
  const lastSentRef = useRef<number>(0);

  useEffect(() => {
    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  const start = () => {
    if (!('geolocation' in navigator)) {
      throw new Error('Geolocation not supported');
    }
    if (watchIdRef.current !== null) return;

    watchIdRef.current = navigator.geolocation.watchPosition(async (pos) => {
      const now = Date.now();
      if (now - lastSentRef.current < intervalMs) return; // throttle
      lastSentRef.current = now;

      const payload = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
        speed: pos.coords.speed,
        recorded_at: new Date(pos.timestamp).toISOString(),
      };

      try {
        await apiClient.post(`/trips/${tripId}/location/`, payload);
      } catch {
        // swallow errors for now; UI should surface them
        console.error('Failed to send location');
      }
    }, (err) => {
      console.error('Geolocation error', err);
    }, { enableHighAccuracy: true, maximumAge: 1000, timeout: 10000 });
  };

  const stop = () => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
  };

  return { start, stop, isRunning: () => watchIdRef.current !== null };
}
