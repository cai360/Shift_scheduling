import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpInterceptor } from '@angular/common/http';


const apiBaseUrl = 'http://localhost:5050/api';
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([
        (request, next) => {
          const inFullUrl = request.url.startsWith('http');
          const newRequest = inFullUrl ? request : request.clone({ url: `${apiBaseUrl}/${request.url}` });
          return next(newRequest);
        },

      ])
    )  
  ]
};
