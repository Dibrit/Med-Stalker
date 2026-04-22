import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class TokenService {

  private ACCESS_KEY = 'access_token';
  private REFRESH_KEY = 'refresh_token';

  setTokens(access: string, refresh: string) {
    localStorage.setItem(this.ACCESS_KEY, access);
    localStorage.setItem(this.REFRESH_KEY, refresh);
  }

  getAccess(): string | null {
    return localStorage.getItem(this.ACCESS_KEY);
  }

  getRefresh(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  clear() {
    localStorage.removeItem(this.ACCESS_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
  }
}