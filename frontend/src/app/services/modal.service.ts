import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ModelService {
  private loadCount = 0;
  private _loading = new BehaviorSubject<boolean>(false);
  loading$ = this._loading.asObservable();

  startLoading(): void{
    this.loadCount++;
    if(this.loadCount === 1){
      this._loading.next(true);
    }
  }

  stopLoading(): void{
    this.loadCount--;
    if(this.loadCount <= 0){
      this._loading.next(false);
    }
  }

  get isLoading(): boolean{
    return this._loading.value;
  }

  private _messages = new BehaviorSubject<{type: string, text: string} | null>(null);
  messages$ = this._messages.asObservable();

  push(type: 'success' | 'error' | 'warning' | 'info', text: string) {
    this._messages.next({ type, text });
  }

  success(text: string) { this.push('success', text); }
  error(text: string) { this.push('error', text); }
  warning(text: string) { this.push('warning', text); }
  info(text: string) { this.push('info', text); }

}
