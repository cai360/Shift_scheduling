import { Routes } from '@angular/router';
import { LoginComponent } from './login/login-component';
import { Index } from './index/index';
import { Dashboard } from './dashboard/dashboard';
import { AuthGuard } from './services/auth.guard';

export const routes: Routes = [
    {path: '', component: Index},
    {path: 'dashboard', component: Dashboard, canActivate: [AuthGuard]},
    {path: '', redirectTo: 'dashboard', pathMatch: 'full'},
     
];
