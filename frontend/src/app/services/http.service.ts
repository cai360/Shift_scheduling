import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { HttpUtils }  from '../model/utils';
import { Result } from '../model/base.model';

@Injectable({
  providedIn: 'root'
})
export class HttpService {
  private http = inject(HttpClient);

  doGet<T>(url:string, params: any = null): Observable<T | null> {
    const fullUrl = HttpUtils.toGetUrl(url, params);
    return this.http.get<Result<T>>(fullUrl).pipe(map(rs => rs.data));
  }

  doGetSilence<T>(url:string, params: any = null): Observable<T | null> {
    const fullUrl = HttpUtils.toGetUrl(url, params);
    const headers = new HttpHeaders({'NO_LOADING':'true'});
    return this.http.get<Result<T>>(fullUrl, { headers}).pipe(map(rs => rs.data));
  }

  doPost<T>(url: string, data: any):Observable<T | null> {
    return this.http.post<Result<T>>(url, data).pipe(map(rs => rs.data));
  }

  doPostSilence<T>(url: string, data: any): Observable<T | null> {
    const headers = new HttpHeaders({'NO_LOADING':'true'});
    return this.http.post<Result<T>>(url, data, { headers }).pipe(map(rs => rs.data));
  }

  doPatch<T>(url: string, data: any):Observable<T | null> {
    return this.http.patch<Result<T>>(url, data).pipe(map(rs => rs.data));
  }

  doDelete<T>(url: string, params: any = null):Observable<T | null> {
    const fullUrl = HttpUtils.toGetUrl(url, params);
    return this.http.delete<Result<T>>(fullUrl).pipe(map(rs => rs.data));
  }

  doDownload(url: string, params: any = null): Observable<Blob> {
    const fullUrl = HttpUtils.toGetUrl(url, params);
    return this.http.get(fullUrl, { responseType: 'blob' });
  }

}
