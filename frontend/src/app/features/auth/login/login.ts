import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth';
import { TokenService } from '../../../core/services/token';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html'
})
export class LoginComponent {

  username = '';
  password = '';

  error = '';

  constructor(
    private auth: AuthService,
    private token: TokenService,
    private router: Router
  ) {}

  login() {
    this.error = '';

    this.auth.login({
      username: this.username,
      password: this.password
    }).subscribe({
      next: (res: any) => {
        this.token.setTokens(res.access, res.refresh);

        const role = 'doctor'; 

        localStorage.setItem('user', JSON.stringify({ role }));
        if (role === 'doctor') {
          this.router.navigate(['/patients']);
        } else {
          this.router.navigate(['/my-records']);
        }
      },

      error: () => {
        this.error = 'Invalid username or password';
      }
    });
  }
}