import { authGuard } from './core/auth/auth.guard';
import { routes } from './app.routes';

describe('app routes', () => {
  it('should include a dedicated diagnoses page', () => {
    const route = routes.find((candidate) => candidate.path === 'diagnoses');

    expect(route).toBeTruthy();
    expect(route?.canActivate).toContain(authGuard);
  });

  it('should include a dedicated prescriptions page', () => {
    const route = routes.find((candidate) => candidate.path === 'prescriptions');

    expect(route).toBeTruthy();
    expect(route?.canActivate).toContain(authGuard);
  });
});
