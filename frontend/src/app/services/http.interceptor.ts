import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { catchError, finalize, switchMap, throwError, filter, take, Subject } from 'rxjs';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { ModelService } from '../services/modal.service';

let isRefreshing = false;
let refreshDone$ = new Subject<boolean>();

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const modal = inject(ModelService);
  const auth = inject(AuthService);

  if (!req.url.startsWith('http')) {
    req = req.clone({ url: `http://localhost:5050/api/${req.url}` });
  }

  const isAuthEndpoint = /\/auth\/(login|refresh|logout)/.test(req.url);

  const token = auth.getAccessToken();
  let authReq = req;
  if (token && !isAuthEndpoint) {
    authReq = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }

  const skipLoading = authReq.headers.get('NO_LOADING_TAG')?.toLowerCase() === 'true';
  if (authReq.headers.has('NO_LOADING_TAG')) {
    authReq = authReq.clone({ headers: authReq.headers.delete('NO_LOADING_TAG') });
  }
  if (!skipLoading) modal.startLoading();

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      const body = error.error;
      const msg =
        body?.message ??
        (error.status === 0
          ? 'Cannot connect to server. Please try again later.'
          : `Error ${error.status}: ${error.statusText}`);

      if (error.status === 401 && !isAuthEndpoint) {
        const refreshToken = auth.getRefreshToken();

        if (!refreshToken) {
          modal.error('Please login again.');
          auth.logout();
          router.navigate(['/login'], { queryParams: { redirect: router.url } });
          return throwError(() => error);
        }

        if (!isRefreshing) {
          isRefreshing = true;

          return auth.refreshAccessToken().pipe(
            switchMap(() => {
              isRefreshing = false;
              refreshDone$.next(true);
              refreshDone$.complete();
              refreshDone$ = new Subject<boolean>(); // reset stream

              const newToken = auth.getAccessToken();
              const retry = authReq.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` },
              });
              return next(retry);
            }),
            catchError((err) => {
              isRefreshing = false;
              refreshDone$.next(false);
              refreshDone$.complete();
              refreshDone$ = new Subject<boolean>();

              modal.error('Session expired. Please login again.');
              auth.logout();
              router.navigate(['/login'], { queryParams: { redirect: router.url } });
              return throwError(() => err);
            })
          );
        } else {
          // 其他請求等待 refresh 完成
          return refreshDone$.pipe(
            take(1),
            switchMap((ok) => {
              if (!ok) return throwError(() => new Error('Token refresh failed'));
              const newToken = auth.getAccessToken();
              const retry = authReq.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` },
              });
              return next(retry);
            })
          );
        }
      }

      if (error.status === 403) {
        modal.error('You do not have permission to perform this action.');
      } else {
        modal.error(msg);
      }

      return throwError(() => error);
    }),
    finalize(() => {
      if (!skipLoading) modal.stopLoading();
    })
  );
};