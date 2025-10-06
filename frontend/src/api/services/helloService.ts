import { apiClient } from '../client';

export interface HelloResponse {
  message: string;
  status: string;
  timestamp: string;
}

export async function getHelloMessage(): Promise<HelloResponse> {
  const { data } = await apiClient.get<HelloResponse>('/hello');
  return data;
}
