import { Component } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup, Form, FormControl } from '@angular/forms';
import { ModelService } from '../services/modal.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule],
  templateUrl: './login-component.html',
  styleUrl: './login-component.scss'
})
export class LoginComponent {
  loginForm!: FormGroup;

  constructor(private fb: FormBuilder,
               private model: ModelService,
              private authService: AuthService,
              private router: Router) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.minLength(6)]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
    
  }

  

  onSubmit() {
    this.authService.login(this.loginForm.value.email, this.loginForm.value.password).subscribe({
      next: (res) => {
        this.model.success('Login successful!');
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.model.error('Login failed!');
      }
    });

    const {email, password} = this.loginForm.value;
    console.log(email, password);

  }

  //'{"email":"user@test.com","password":"Password001"

}
