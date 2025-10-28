import { Injectable, inject } from '@angular/core';
import { HttpService } from './http.service';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: { id: number; email: string; name: string };
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpService);
  private router = inject(Router);

  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  login(email: string, password: string) {
    return this.http
      .doPost<LoginResponse>('auth/login', { email, password })
      .pipe(
        tap((res) => {
          if (res) {
            this.saveTokens(res.access_token, res.refresh_token);
          }
        })
      );
  }

  logout() {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    this.router.navigate(['/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  saveTokens(access: string, refresh: string) {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  refreshAccessToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) throw new Error('No refresh token');
    return this.http
      .doPost<LoginResponse>('auth/refresh', { refresh_token: refreshToken })
      .pipe(
        tap((res) => {
          if (res?.access_token) {
            localStorage.setItem(this.ACCESS_TOKEN_KEY, res.access_token);
          }
        })
      );
  }
}