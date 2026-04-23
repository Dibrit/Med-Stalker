import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, finalize, of, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { ToastService } from '../../shared/toast/toast.service';

function isAuthFreeUrl(url: string): boolean {
  return (
    url.includes('/auth/login/') ||
    url.includes('/auth/register/') ||
    url.includes('/auth/refresh/')
  );
}

let refreshInFlight: Observable<{ access: string }> | null = null;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const toasts = inject(ToastService);

  const access = auth.accessToken();
  const shouldAttach = !!access && !isAuthFreeUrl(req.url);

  const authedReq = shouldAttach
    ? req.clone({ setHeaders: { Authorization: `Bearer ${access}` } })
    : req;

  return next(authedReq).pipe(
    catchError((err: unknown) => {
      if (!(err instanceof HttpErrorResponse)) return throwError(() => err);
      if (err.status !== 401) return throwError(() => err);
      if (isAuthFreeUrl(req.url)) return throwError(() => err);

      const refresh = auth.refreshToken();
      if (!refresh) return throwError(() => err);

      if (!refreshInFlight) {
        refreshInFlight = auth.refreshAccess().pipe(
          finalize(() => {
            refreshInFlight = null;
          })
        );
      }

      return refreshInFlight.pipe(
        switchMap(() => {
          const newAccess = auth.accessToken();
          if (!newAccess) return throwError(() => err);
          const retry = req.clone({ setHeaders: { Authorization: `Bearer ${newAccess}` } });
          return next(retry);
        }),
        catchError((refreshErr) => {
          auth.clearTokens();
          toasts.error('Session expired. Please log in again.');
          router.navigate(['/login'], { queryParams: { reason: 'expired' } });
          return throwError(() => refreshErr);
        })
      );
    })
  );
};

