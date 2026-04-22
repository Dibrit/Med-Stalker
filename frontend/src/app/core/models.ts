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
  diagnosis: number | null;
  medication_name?: string | null;
  instructions: string;
  issued_at: string;
  valid_until: string | null;
  created_at: string;
  updated_at: string;
}

