import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private loggedIn : boolean = false;

  login(){
    this.loggedIn = true;
  }

  logout(){
    this.loggedIn = false;
  }

  isloggedIn(): boolean {
    return this.loggedIn;
  }
  
}
