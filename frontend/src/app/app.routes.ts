import { Routes } from '@angular/router';
import { LoginComponent } from './login/login-component';
import { Index } from './index/index';
//improt { DashboardComponent } from './dashboard/dashboard.component';
import { AuthGuard } from './services/auth.guard';

export const routes: Routes = [
    {path: '', component: Index},
    //{path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard]},
     
];
