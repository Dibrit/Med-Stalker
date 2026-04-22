import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type ToastKind = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  kind: ToastKind;
  message: string;
  title?: string;
  createdAt: number;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly _toasts = new BehaviorSubject<Toast[]>([]);
  readonly toasts$ = this._toasts.asObservable();

  show(kind: ToastKind, message: string, opts?: { title?: string; timeoutMs?: number }) {
    const toast: Toast = {
      id: crypto.randomUUID(),
      kind,
      message,
      title: opts?.title,
      createdAt: Date.now()
    };
    this._toasts.next([toast, ...this._toasts.value].slice(0, 5));

    const timeoutMs = opts?.timeoutMs ?? 4500;
    window.setTimeout(() => this.dismiss(toast.id), timeoutMs);
  }

  success(message: string, opts?: { title?: string; timeoutMs?: number }) {
    this.show('success', message, opts);
  }
  error(message: string, opts?: { title?: string; timeoutMs?: number }) {
    this.show('error', message, opts);
  }
  info(message: string, opts?: { title?: string; timeoutMs?: number }) {
    this.show('info', message, opts);
  }
  warning(message: string, opts?: { title?: string; timeoutMs?: number }) {
    this.show('warning', message, opts);
  }

  dismiss(id: string) {
    this._toasts.next(this._toasts.value.filter((t) => t.id !== id));
  }

  clear() {
    this._toasts.next([]);
  }
}

