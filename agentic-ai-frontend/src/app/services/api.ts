import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { SearchRequest, SearchResponse, FilePreview } from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000';
  private readonly httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  search(request: SearchRequest): Observable<SearchResponse> {
    return this.http.post<SearchResponse>(
      `${this.baseUrl}/search`,
      request,
      this.httpOptions
    ).pipe(
      catchError(this.handleError)
    );
  }

  previewFile(filePath: string): Observable<FilePreview> {
    return this.http.get<FilePreview>(
      `${this.baseUrl}/preview/${encodeURIComponent(filePath)}`
    ).pipe(
      catchError(this.handleError)
    );
  }

  getHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any): Observable<never> {
    console.error('API Error:', error);
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.detail || error.message || 'Server error';
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
