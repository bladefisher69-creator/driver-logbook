export interface Driver {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  license_number: string;
  phone: string;
  is_admin: boolean;
  total_hours_8days: number;
  remaining_hours_8days: number;
  compliance_status: 'compliant' | 'warning' | 'exceeded';
  miles_since_last_fuel: number;
  needs_refuel: boolean;
  created_at: string;
}

export interface Trip {
  id: number;
  driver: number;
  driver_name: string;
  vehicle_id: string;
  origin: string;
  destination: string;
  pickup_lat?: number | null;
  pickup_lng?: number | null;
  destination_lat?: number | null;
  destination_lng?: number | null;
  distance: number;
  start_time: string;
  end_time: string | null;
  pickup_time: number;
  dropoff_time: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  notes: string;
  total_trip_hours: number;
  driver_hours_after_trip: number;
  compliance_errors: string[];
  created_at: string;
  updated_at: string;
}

export interface FuelLog {
  id: number;
  driver: number;
  driver_name: string;
  trip: number | null;
  fuel_type: 'diesel' | 'gasoline' | 'electric' | 'hybrid';
  fuel_amount: number;
  fuel_cost: number;
  cost_per_gallon: number;
  odometer_reading: number;
  location: string;
  timestamp: string;
  notes: string;
  created_at: string;
}

export interface ComplianceReport {
  id: number;
  driver: number;
  driver_name: string;
  date_start: string;
  date_end: string;
  total_hours: number;
  total_miles: number;
  trip_count: number;
  limit_exceeded: boolean;
  refuel_violations: number;
  notes: string;
  generated_at: string;
}

export interface DashboardStats {
  total_drivers: number;
  active_trips: number;
  completed_trips_today: number;
  compliance_violations: number;
  drivers_needing_refuel: number;
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  license_number: string;
  phone?: string;
}
