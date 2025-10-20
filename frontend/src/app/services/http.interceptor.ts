import { HttpErrorResponse,  HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { catchError, finalize, tap, throwError } from 'rxjs';
import { ModelService } from '../services/modal.service';
import { inject} from '@angular/core';
import { Router } from '@angular/router';


export const authInterceptor: HttpInterceptorFn = (request: HttpRequest<any>, next) => {
    const router = inject(Router);
    const modal = inject(ModelService);

    if (!request.url.startsWith('http')) {
        request = request.clone({ url: `http://localhost:5050/api/${request.url}` });
    }

    const token = localStorage.getItem('token');
    let cloneRequest = request;
    if(token){
        cloneRequest = request.clone({
            setHeaders: { Authorization: `Bearer ${token}` }
        });
    }

    const skipLoading = request.headers.get('NO_LOADING_TAG')?.toLowerCase() === 'true';
    cloneRequest = cloneRequest.clone({
        headers: cloneRequest.headers.delete('NO_LOADING_TAG'),
    });
    if(!skipLoading) modal.startLoading();

    return next(cloneRequest).pipe(
        catchError((error: HttpErrorResponse) => {
            const body = error.error;
            const msg = body?.message ??
            (error.status === 0) ? 'Cannot connect to server. Please try again later.' : 'Error $`{error.status}: ${error.statusText}';
           modal.error(msg);

            if (error.status === 401) {
                localStorage.removeItem('access_token');
                router.navigate(['/login']);
            }else if (error.status === 403) {
                modal.error('You do not have permission to perform this action.');
            }
            return throwError(() => error);
        }),
        finalize(() => {
            if (!skipLoading) modal.stopLoading();
        })
    )
}


