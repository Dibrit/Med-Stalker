import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, catchError, map, of, tap } from 'rxjs';
import { Patient } from '../models';
import { PatientService } from '../patients/patient.service';

export type UserMode = 'unknown' | 'doctor' | 'patient';

export interface SessionState {
  mode: UserMode;
  selfPatient: Patient | null;
}

@Injectable({ providedIn: 'root' })
export class SessionService {
  private readonly patients = inject(PatientService);

  private readonly _state = new BehaviorSubject<SessionState>({ mode: 'unknown', selfPatient: null });
  readonly state$ = this._state.asObservable();

  snapshot(): SessionState {
    return this._state.value;
  }

  clear() {
    this._state.next({ mode: 'unknown', selfPatient: null });
  }

  /**
   * Infer doctor vs patient by calling GET patients/:
   * - >1 => doctor
   * - 1 => patient (self)
   *
   * If inference fails, keep mode "unknown" (UI should degrade gracefully).
   */
  hydrate(): Observable<SessionState> {
    return this.patients.list().pipe(
      map((list) => {
        const mode: UserMode = list.length > 1 ? 'doctor' : list.length === 1 ? 'patient' : 'unknown';
        const selfPatient = list.length === 1 ? list[0] : null;
        return { mode, selfPatient };
      }),
      tap((s) => this._state.next(s)),
      catchError(() => {
        const fallback: SessionState = { mode: 'unknown', selfPatient: null };
        this._state.next(fallback);
        return of(fallback);
      })
    );
  }
}

