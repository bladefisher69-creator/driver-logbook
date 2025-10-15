import React, { useEffect, useState } from 'react';
import { Users, Truck, AlertTriangle, CheckCircle, Fuel as FuelIcon } from 'lucide-react';
import { apiClient } from '../../api/client';
import { DashboardStats, Driver, Trip } from '../../types';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [activeTrips, setActiveTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, driversData, tripsData] = await Promise.all([
        apiClient.get<DashboardStats>('/dashboard/stats/'),
        apiClient.get<{ results: Driver[] }>('/drivers/'),
        apiClient.get<{ results: Trip[] }>('/trips/active/'),
      ]);

      setStats(statsData);
      setDrivers(driversData.results || []);
      setActiveTrips(tripsData.results || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
        <p className="text-slate-600 mt-1">Overview of all driver activities and compliance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-8 h-8 text-blue-600" />
            <span className="text-3xl font-bold text-slate-900">{stats?.total_drivers || 0}</span>
          </div>
          <div className="text-sm font-medium text-slate-700">Total Drivers</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <Truck className="w-8 h-8 text-emerald-600" />
            <span className="text-3xl font-bold text-slate-900">{stats?.active_trips || 0}</span>
          </div>
          <div className="text-sm font-medium text-slate-700">Active Trips</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-8 h-8 text-teal-600" />
            <span className="text-3xl font-bold text-slate-900">{stats?.completed_trips_today || 0}</span>
          </div>
          <div className="text-sm font-medium text-slate-700">Completed Today</div>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <span className="text-3xl font-bold text-red-900">{stats?.compliance_violations || 0}</span>
          </div>
          <div className="text-sm font-medium text-red-700">Compliance Violations</div>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <FuelIcon className="w-8 h-8 text-amber-600" />
            <span className="text-3xl font-bold text-amber-900">{stats?.drivers_needing_refuel || 0}</span>
          </div>
          <div className="text-sm font-medium text-amber-700">Need Refuel</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Driver Compliance Status</h2>
          {drivers.length === 0 ? (
            <p className="text-slate-600 text-center py-8">No drivers registered</p>
          ) : (
            <div className="space-y-3">
              {drivers.slice(0, 10).map((driver) => (
                <div key={driver.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-slate-900">{driver.full_name}</div>
                    <div className="text-sm text-slate-600">
                      {driver.total_hours_8days}h / 70h ({driver.remaining_hours_8days}h remaining)
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {driver.needs_refuel && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        <FuelIcon className="w-3 h-3 mr-1" />
                        Refuel
                      </span>
                    )}
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        driver.compliance_status === 'exceeded'
                          ? 'bg-red-100 text-red-800'
                          : driver.compliance_status === 'warning'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {driver.compliance_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Active Trips</h2>
          {activeTrips.length === 0 ? (
            <p className="text-slate-600 text-center py-8">No active trips</p>
          ) : (
            <div className="space-y-3">
              {activeTrips.map((trip) => (
                <div key={trip.id} className="p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-slate-900">{trip.driver_name}</div>
                    <span className="text-xs font-mono text-slate-600">{trip.vehicle_id}</span>
                  </div>
                  <div className="text-sm text-slate-600">
                    {trip.origin} → {trip.destination}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-slate-500">{trip.distance} miles</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      In Progress
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
