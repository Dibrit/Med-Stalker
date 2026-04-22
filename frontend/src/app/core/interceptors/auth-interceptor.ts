import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { TokenService } from '../services/token';

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  if (typeof window === 'undefined') return next(req);

  const token = localStorage.getItem('access');

  if (!token) return next(req);

  const cloned = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });

  return next(cloned);
};