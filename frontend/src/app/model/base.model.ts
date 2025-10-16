// Base API response interfaces to match backend format

// For single resource responses (users, shifts, etc.)
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

// For list responses
export interface ApiListResponse<T> {
  data: T[];
  error?: string;
}

// For authentication responses
export interface AuthResponse {
  user: any; // You can define a proper User interface
  access_token: string;
  refresh_token: string;
  error?: string;
}

// Generic error response
export interface ErrorResponse {
  error: string;
}