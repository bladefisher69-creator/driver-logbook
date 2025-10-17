import React, { useEffect, useState, useCallback } from 'react';
import { Clock, MapPin, Fuel, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { apiClient } from '../../api/client';
import { Trip } from '../../types';

export const DriverDashboard: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [recentTrips, setRecentTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const tripsData = await apiClient.get<{ results: Trip[] }>('/trips/?limit=5');
      setRecentTrips(tripsData.results || []);
      await refreshUser();
    } catch {
      console.error('Failed to load dashboard data:');
    } finally {
      setIsLoading(false);
    }
  }, [refreshUser]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'exceeded':
        return 'text-red-600 bg-red-50';
      case 'warning':
        return 'text-amber-600 bg-amber-50';
      default:
        return 'text-green-600 bg-green-50';
    }
  };

  const getComplianceIcon = (status: string) => {
    switch (status) {
      case 'exceeded':
        return <AlertTriangle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <CheckCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.first_name}!</h1>
        <p className="text-slate-600 mt-1">Here's your logbook overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-slate-900">{user?.total_hours_8days}h</span>
          </div>
          <div className="text-sm text-slate-600">Hours (8 Days)</div>
          <div className="mt-2 text-xs text-slate-500">{user?.remaining_hours_8days}h remaining</div>
        </div>

        <div className={`rounded-xl shadow-sm border p-6 ${getComplianceColor(user?.compliance_status || 'compliant')}`}>
          <div className="flex items-center justify-between mb-2">
            {getComplianceIcon(user?.compliance_status || 'compliant')}
            <span className="text-sm font-semibold uppercase">{user?.compliance_status}</span>
          </div>
          <div className="text-sm font-medium">Compliance Status</div>
          <div className="mt-2 text-xs">
            {user?.compliance_status === 'exceeded'
              ? 'Hour limit exceeded'
              : user?.compliance_status === 'warning'
              ? 'Approaching limit'
              : 'All clear'}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <MapPin className="w-8 h-8 text-emerald-600" />
            <span className="text-2xl font-bold text-slate-900">{user?.miles_since_last_fuel}</span>
          </div>
          <div className="text-sm text-slate-600">Miles Since Refuel</div>
          <div className="mt-2 text-xs text-slate-500">
            {1000 - (user?.miles_since_last_fuel || 0)} miles until refuel
          </div>
        </div>

        <div className={`rounded-xl shadow-sm border p-6 ${user?.needs_refuel ? 'bg-red-50 text-red-600' : 'bg-white text-slate-900'}`}>
          <div className="flex items-center justify-between mb-2">
            <Fuel className="w-8 h-8" />
            <span className="text-sm font-semibold uppercase">{user?.needs_refuel ? 'REQUIRED' : 'OK'}</span>
          </div>
          <div className="text-sm font-medium">Refuel Status</div>
          <div className="mt-2 text-xs">
            {user?.needs_refuel ? 'Refuel before next trip' : 'No refuel needed'}
          </div>
        </div>
      </div>

      {user?.needs_refuel && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-900">Refueling Required</h3>
              <p className="text-sm text-red-700 mt-1">
                You have driven {user.miles_since_last_fuel} miles since your last refuel. Please refuel before starting
                your next trip.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Recent Trips</h2>
        {recentTrips.length === 0 ? (
          <p className="text-slate-600 text-center py-8">No trips recorded yet</p>
        ) : (
          <div className="space-y-3">
            {recentTrips.map((trip) => (
              <div key={trip.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-slate-900">
                    {trip.origin} → {trip.destination}
                  </div>
                  <div className="text-sm text-slate-600 mt-1">
                    {trip.distance} miles • {trip.total_trip_hours}h • {trip.vehicle_id}
                  </div>
                </div>
                <div>
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      trip.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : trip.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-slate-100 text-slate-800'
                    }`}
                  >
                    {trip.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
