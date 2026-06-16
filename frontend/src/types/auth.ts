export interface User {
  id: string;
  username: string;
  balance: number;
  equity: number;
  createdAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface TwoFAEnableResponse {
  message: string;
  secret: string;
}

export interface TwoFAVerifyRequest {
  code: string;
}

export type UserRole = 'admin' | 'trader' | 'viewer';

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<TokenResponse>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  enable2FA: () => Promise<TwoFAEnableResponse>;
  verify2FA: (code: string) => Promise<void>;
  refreshToken: () => Promise<void>;
}
