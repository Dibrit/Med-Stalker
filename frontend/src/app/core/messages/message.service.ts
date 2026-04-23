import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { apiUrl } from '../api';
import { Message } from '../models';

export interface MessageCreateRequest {
  recipient_patient?: number | null;
  recipient_doctor?: number | null;
  content: string;
}

export type MessageUpdateRequest = Partial<MessageCreateRequest>;

@Injectable({ providedIn: 'root' })
export class MessageService {
  private readonly http = inject(HttpClient);

  list(): Observable<Message[]> {
    return this.http.get<Message[]>(apiUrl('messages/'));
  }

  get(id: number): Observable<Message> {
    return this.http.get<Message>(apiUrl(`messages/${id}/`));
  }

  create(req: MessageCreateRequest): Observable<Message> {
    return this.http.post<Message>(apiUrl('messages/'), req);
  }

  update(id: number, req: MessageUpdateRequest): Observable<Message> {
    return this.http.patch<Message>(apiUrl(`messages/${id}/`), req);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(apiUrl(`messages/${id}/`));
  }
}
