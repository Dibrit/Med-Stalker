export interface AuthResponse {
  access: string;
  refresh: string;
}

export interface Patient {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  phone: string | null;
  medical_record_number: string;
  created_at: string;
  updated_at: string;
}

export interface RegisterResponse extends AuthResponse {
  patient: Patient;
}

export interface Diagnosis {
  id: number;
  patient: Patient;
  recorded_by_id: number;
  recorded_by_name: string;
  title: string;
  description?: string | null;
  icd_code?: string | null;
  status?: string | null;
  diagnosed_at: string;
  created_at: string;
  updated_at: string;
}

export interface Prescription {
  id: number;
  patient: Patient;
  prescribed_by_id: number;
  prescribed_by_name: string;
  diagnosis: number | null;
  medication_name?: string | null;
  instructions: string;
  issued_at: string;
  valid_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface Doctor {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  specialization: string;
  license_number: string;
  created_at: string;
  updated_at: string;
}

export interface Appointment {
  id: number;
  patient: Patient;
  doctor: Doctor;
  status: 'requested' | 'confirmed' | 'cancelled' | 'completed';
  reason?: string | null;
  starts_at: string;
  ends_at: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  sender_type: 'patient' | 'doctor';
  sender_patient: number | null;
  sender_doctor: number | null;
  recipient_patient: number | null;
  recipient_doctor: number | null;
  sender_name: string;
  recipient_name: string;
  content: string;
  is_read: boolean;
  created_at: string;
  updated_at: string;
}
