import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { SessionService } from './session.service';
import { ToastService } from '../../shared/toast/toast.service';
import { map } from 'rxjs';

export const doctorGuard: CanActivateFn = () => {
  const session = inject(SessionService);
  const router = inject(Router);
  const toasts = inject(ToastService);

  const snap = session.snapshot();
  if (snap.mode === 'doctor') return true;
  if (snap.mode === 'unknown') {
    return session.hydrate().pipe(
      map((s) => {
        if (s.mode === 'doctor') return true;
        toasts.warning('Doctor access required.');
        return router.createUrlTree(['/my-records']);
      })
    );
  }

  toasts.warning('Doctor access required.');
  return router.createUrlTree(['/my-records']);
};

