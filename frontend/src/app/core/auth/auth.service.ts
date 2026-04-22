import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, catchError, map, of, switchMap, tap, throwError } from 'rxjs';
import { apiUrl } from '../api';
import { DrfErrorPayload } from '../api-errors';
import { AuthResponse, RegisterResponse } from '../models';

const LS_ACCESS = 'medstalker.access';
const LS_REFRESH = 'medstalker.refresh';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  date_of_birth?: string | null;
  phone?: string | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly _authed = new BehaviorSubject<boolean>(!!this.accessToken());
  readonly isAuthenticated$ = this._authed.asObservable();

  accessToken(): string | null {
    return localStorage.getItem(LS_ACCESS);
  }

  refreshToken(): string | null {
    return localStorage.getItem(LS_REFRESH);
  }

  setTokens(tokens: AuthResponse) {
    localStorage.setItem(LS_ACCESS, tokens.access);
    localStorage.setItem(LS_REFRESH, tokens.refresh);
    this._authed.next(true);
  }

  clearTokens() {
    localStorage.removeItem(LS_ACCESS);
    localStorage.removeItem(LS_REFRESH);
    this._authed.next(false);
  }

  login(req: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(apiUrl('auth/login/'), req).pipe(
      tap((res) => this.setTokens(res))
    );
  }

  register(req: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(apiUrl('auth/register/'), req).pipe(
      tap((res) => this.setTokens({ access: res.access, refresh: res.refresh }))
    );
  }

  refreshAccess(): Observable<{ access: string }> {
    const refresh = this.refreshToken();
    if (!refresh) return throwError(() => new Error('No refresh token.'));
    return this.http.post<{ access: string }>(apiUrl('auth/refresh/'), { refresh }).pipe(
      tap((res) => localStorage.setItem(LS_ACCESS, res.access))
    );
  }

  logout(): Observable<{ detail: string } | null> {
    const refresh = this.refreshToken();
    if (!refresh) {
      this.clearTokens();
      return of(null);
    }
    return this.http.post<{ detail: string }>(apiUrl('auth/logout/'), { refresh }).pipe(
      catchError(() => of(null)),
      tap(() => this.clearTokens())
    );
  }

  /** Convenience for components to map DRF error payloads. */
  asDrfError(err: unknown): DrfErrorPayload {
    const anyErr = err as any;
    return anyErr?.error ?? anyErr ?? {};
  }
}

