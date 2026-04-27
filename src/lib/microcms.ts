import { createClient } from 'microcms-js-sdk';

const serviceDomain = import.meta.env.MICROCMS_SERVICE_DOMAIN ?? 'dummy';
const apiKey = import.meta.env.MICROCMS_API_KEY ?? 'dummy';

export const client = createClient({ serviceDomain, apiKey });

// 型定義
export type News = {
  id: string;
  createdAt: string;
  updatedAt: string;
  publishedAt: string;
  title: string;
  category: string;
  body: string;
  thumbnail?: { url: string; width: number; height: number };
};

export type Organization = {
  id: string;
  name: string;
  description: string;
  category: string;
  area: string;
  url?: string;
  logo?: { url: string; width: number; height: number };
};

export type Subsidy = {
  id: string;
  title: string;
  summary: string;
  target: string;
  amount?: string;
  deadline?: string;
  url?: string;
  category: string;
};

export type ListResponse<T> = {
  contents: T[];
  totalCount: number;
  offset: number;
  limit: number;
};
