import { Component } from '@angular/core';
import { LoginComponent } from "../login/login-component";

@Component({
  selector: 'app-index',
  imports: [LoginComponent],
  templateUrl: './index.html',
  styleUrl: './index.scss'
})
export class Index {

}
