import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UploadResponse {
  message: string;
  doc_id: string;
  total_chunks: number;
  document_length: number;
}

export interface AskResponse {
  doc_id: string;
  answer: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${this.baseUrl}/upload`, formData);
  }

  askQuestion(question: string, docId: string): Observable<AskResponse> {
    const formData = new FormData();
    formData.append('question', question);
    formData.append('doc_id', docId);

    return this.http.post<AskResponse>(`${this.baseUrl}/ask`, formData);
  }
}
