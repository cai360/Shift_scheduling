import { Injectable, inject } from '@angular/core';
import { HttpService } from './http.service';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';


interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: {id: number, email: string, name: string};
}

@Injectable({
  providedIn: 'root'
})


export class Auth {
  private http = inject(HttpService);
  private router = inject(Router);

  private loggedIn = false;
  private ACCESS_TOKEN_KEY = 'access_token';
  private REFRESH_TOKEN_KEY = 'refresh_token';

  login(email: string, password: string){
    return this.http.doPost<LoginResponse>('auth/login', {email, password}).pipe(
      tap (res =>{
        if(res){
          localStorage.setItem(this.ACCESS_TOKEN_KEY, res.access_token);
          localStorage.setItem(this.REFRESH_TOKEN_KEY, res.refresh_token);
          this.loggedIn = true;
        }
      })
    )

  }

  logout(){
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    this.loggedIn = false;
    this.router.navigate(['/login']);
  }

  isloggedIn(): boolean {
    return this.loggedIn;
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }
  
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return !!token;
  }
  
}
