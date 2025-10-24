import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { CanActivate, Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private Auth: AuthService, private Router: Router){};

  canActivate (): boolean {
    if(this.Auth.isloggedIn() == true){
      return true;
    } else {
      this.Router.navigate(['/login']);
      return false;
    }
  }
}

