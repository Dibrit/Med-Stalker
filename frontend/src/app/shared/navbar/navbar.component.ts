import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../toast/toast.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
  readonly auth = inject(AuthService);
  readonly session = inject(SessionService);
  private readonly router = inject(Router);
  private readonly toasts = inject(ToastService);

  logout() {
    this.auth.logout().subscribe(() => {
      this.session.clear();
      this.toasts.info('Logged out.');
      this.router.navigate(['/login']);
    });
  }
}

