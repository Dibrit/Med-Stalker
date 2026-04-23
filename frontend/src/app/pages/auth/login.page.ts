import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs';
import { fieldErrors, summarizeError } from '../../core/api-errors';
import { AuthService, RegisterRequest } from '../../core/auth/auth.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';

type AuthTab = 'login' | 'register';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.page.html',
  styleUrl: './login.page.scss'
})
export class LoginPage {
  private readonly auth = inject(AuthService);
  private readonly session = inject(SessionService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  tab: AuthTab = 'login';
  loading = false;

  loginModel = { username: '', password: '' };
  loginError: string | null = null;

  registerModel: RegisterRequest = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
    date_of_birth: null,
    phone: null
  };
  registerFieldErrors: Record<string, string[]> = {};
  registerNonFieldError: string | null = null;

  switchTab(tab: AuthTab) {
    this.loginError = null;
    this.registerNonFieldError = null;
    this.registerFieldErrors = {};
    this.tab = tab;
  }

  submitLogin(form: NgForm) {
    if (form.invalid) return;
    this.loading = true;
    this.loginError = null;

    this.auth
      .login(this.loginModel)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: () => {
          this.session.hydrate().subscribe();
          const nextUrl = this.route.snapshot.queryParamMap.get('next');
          this.router.navigateByUrl(nextUrl || '/dashboard');
          this.cdr.detectChanges();
        },
        error: (err) => {
          const payload = this.auth.asDrfError(err);
          this.loginError = summarizeError(payload);
          this.cdr.detectChanges();
        }
      });
  }

  submitRegister(form: NgForm) {
    this.registerNonFieldError = null;
    this.registerFieldErrors = {};

    if (this.registerModel.password !== this.registerModel.password_confirm) {
      this.registerFieldErrors = { password_confirm: ['Passwords do not match.'] };
      return;
    }
    if (form.invalid) return;

    this.loading = true;

    const req: RegisterRequest = {
      username: this.registerModel.username.trim(),
      email: this.registerModel.email.trim(),
      first_name: this.registerModel.first_name.trim(),
      last_name: this.registerModel.last_name.trim(),
      password: this.registerModel.password,
      password_confirm: this.registerModel.password_confirm,
      date_of_birth: this.registerModel.date_of_birth || undefined,
      phone: this.registerModel.phone || undefined
    };

    this.auth
      .register(req)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: () => {
          this.session.hydrate().subscribe();
          this.toasts.success('Account created.');
          this.router.navigateByUrl('/my-records');
          this.cdr.detectChanges();
        },
        error: (err) => {
          const payload = this.auth.asDrfError(err);
          this.registerNonFieldError = summarizeError(payload);
          this.registerFieldErrors = fieldErrors(payload);
          this.cdr.detectChanges();
        }
      });
  }
}

