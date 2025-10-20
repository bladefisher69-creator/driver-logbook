import React, { useState } from 'react';
import { X, AlertCircle } from 'lucide-react';
import { apiClient } from '../../api/client';

interface FuelFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const FuelForm: React.FC<FuelFormProps> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    fuel_type: 'diesel',
    fuel_amount: '',
    fuel_cost: '',
    odometer_reading: '',
    location: '',
    timestamp: new Date().toISOString().slice(0, 16),
    notes: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await apiClient.post('/fuel-logs/', formData);
      onSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err || 'Failed to log fuel');
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Log Refuel</h1>
          <p className="text-slate-600 mt-1">Record a refueling event</p>
        </div>
        <button
          onClick={onClose}
          className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          title="Close"
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
              <label htmlFor="fuel_type" className="block text-sm font-medium text-slate-700 mb-2">
                Fuel Type *
              </label>
              <select
                id="fuel_type"
                name="fuel_type"
                value={formData.fuel_type}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="diesel">Diesel</option>
                <option value="gasoline">Gasoline</option>
                <option value="electric">Electric</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-slate-700 mb-2">
                Location *
              </label>
              <input
                id="location"
                name="location"
                type="text"
                value={formData.location}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Gas Station Name, City"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="fuel_amount" className="block text-sm font-medium text-slate-700 mb-2">
                Fuel Amount (gallons) *
              </label>
              <input
                id="fuel_amount"
                name="fuel_amount"
                type="number"
                step="0.01"
                value={formData.fuel_amount}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="50.00"
              />
            </div>

            <div>
              <label htmlFor="fuel_cost" className="block text-sm font-medium text-slate-700 mb-2">
                Total Cost ($) *
              </label>
              <input
                id="fuel_cost"
                name="fuel_cost"
                type="number"
                step="0.01"
                value={formData.fuel_cost}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="150.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="odometer_reading" className="block text-sm font-medium text-slate-700 mb-2">
                Odometer Reading (miles) *
              </label>
              <input
                id="odometer_reading"
                name="odometer_reading"
                type="number"
                step="0.01"
                value={formData.odometer_reading}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="75000"
              />
            </div>

            <div>
              <label htmlFor="timestamp" className="block text-sm font-medium text-slate-700 mb-2">
                Refuel Time *
              </label>
              <input
                id="timestamp"
                name="timestamp"
                type="datetime-local"
                value={formData.timestamp}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
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
              placeholder="Add any additional notes..."
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
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Logging...' : 'Log Refuel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
