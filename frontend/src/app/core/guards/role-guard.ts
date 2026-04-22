import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const roleGuard = (role: 'doctor' | 'patient'): CanActivateFn => {
  return () => {
    const router = inject(Router);

    const user = JSON.parse(localStorage.getItem('user') || 'null');

    if (!user || user.role !== role) {
      router.navigate(['/login']);
      return false;
    }

    return true;
  };
};