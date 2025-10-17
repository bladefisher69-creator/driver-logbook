import React, { useEffect, useState } from 'react';
import { Plus, MapPin, Calendar, Clock, AlertCircle } from 'lucide-react';
import { apiClient } from '../../api/client';
import { Trip } from '../../types';
import { TripForm } from './TripForm';

export const TripsPage: React.FC = () => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const data = await apiClient.get<{ results: Trip[] }>('/trips/');
      setTrips(data.results || []);
    } catch (error) {
      console.error('Failed to load trips:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = async (tripId: number) => {
    try {
      await apiClient.post(`/trips/${tripId}/complete/`, {
        end_time: new Date().toISOString(),
      });
      await loadTrips();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : (typeof error === 'string' ? error : 'Failed to complete trip');
      alert(msg);
    }
  };

  const handleCancel = async (tripId: number) => {
    if (!confirm('Are you sure you want to cancel this trip?')) return;

    try {
      await apiClient.post(`/trips/${tripId}/cancel/`, {});
      await loadTrips();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : (typeof error === 'string' ? error : 'Failed to cancel trip');
      alert(msg);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading trips...</div>
      </div>
    );
  }

  if (showForm) {
    return (
      <TripForm
        trip={selectedTrip}
        onClose={() => {
          setShowForm(false);
          setSelectedTrip(null);
        }}
        onSuccess={() => {
          setShowForm(false);
          setSelectedTrip(null);
          loadTrips();
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Trip Logs</h1>
          <p className="text-slate-600 mt-1">Manage your trip records</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Trip
        </button>
      </div>

      {trips.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
          <MapPin className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">No trips yet</h3>
          <p className="text-slate-600 mb-6">Start logging your first trip to track your hours</p>
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create First Trip
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Route
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Vehicle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Distance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Start Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {trips.map((trip) => (
                  <tr key={trip.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-start space-x-2">
                        <MapPin className="w-4 h-4 text-slate-400 mt-1 flex-shrink-0" />
                        <div className="text-sm">
                          <div className="font-medium text-slate-900">{trip.origin}</div>
                          <div className="text-slate-600">→ {trip.destination}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-mono text-slate-900">{trip.vehicle_id}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-slate-900">{trip.distance} mi</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span className="text-sm text-slate-900">{trip.total_trip_hours}h</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <span className="text-sm text-slate-900">{formatDate(trip.start_time)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                          trip.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : trip.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-800'
                            : trip.status === 'cancelled'
                            ? 'bg-slate-100 text-slate-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {trip.status.replace('_', ' ')}
                      </span>
                      {trip.compliance_errors && trip.compliance_errors.length > 0 && (
                        <div className="mt-1 flex items-center space-x-1 text-xs text-red-600">
                          <AlertCircle className="w-3 h-3" />
                          <span>Compliance issue</span>
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {trip.status === 'in_progress' && (
                          <>
                            <button
                              onClick={() => handleComplete(trip.id)}
                              className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                            >
                              Complete
                            </button>
                            <button
                              onClick={() => handleCancel(trip.id)}
                              className="text-sm text-red-600 hover:text-red-700 font-medium"
                            >
                              Cancel
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
