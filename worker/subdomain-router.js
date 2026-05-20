/**
 * hinokunimirai.com サブドメインルーター
 *
 * サブドメイン (例: nankan.hinokunimirai.com) へのアクセスを
 * メインサイトの団体詳細ページ (hinokunimirai.com/organizations/[slug])
 * にプロキシします。URL はサブドメインのまま維持されます。
 *
 * Cloudflare Workers にデプロイして使用してください。
 * Worker Route: *hinokunimirai.com/*
 */

const MAIN_SITE = 'https://hinokunimirai.com';

// サブドメイン → 団体スラッグ マッピング
// microCMS に subdomain フィールドを追加した場合、このマップも更新してください
const SUBDOMAIN_MAP = {
  'nankan': 'nankan',
  // 例: 'tamana': 'tamana',
  // 例: 'arao': 'arao',
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const hostname = url.hostname; // 例: nankan.hinokunimirai.com

    // メインドメイン (www または apex) はそのままパススルー
    if (hostname === 'hinokunimirai.com' || hostname === 'www.hinokunimirai.com') {
      return fetch(request);
    }

    // サブドメインを抽出
    const parts = hostname.split('.');
    if (parts.length < 3) {
      return fetch(request);
    }
    const subdomain = parts[0]; // 例: 'nankan'

    // マッピングにないサブドメインは 404
    const slug = SUBDOMAIN_MAP[subdomain];
    if (!slug) {
      return new Response(`サブドメイン "${subdomain}" は登録されていません。`, {
        status: 404,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      });
    }

    // メインサイトの団体ページへプロキシ
    const targetPath = `/organizations/${slug}${url.pathname === '/' ? '' : url.pathname}${url.search}`;
    const targetUrl = `${MAIN_SITE}${targetPath}`;

    const proxyRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: 'follow',
    });

    const response = await fetch(proxyRequest);

    // レスポンスヘッダーをコピーして返す
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Served-By', 'hinokunimirai-subdomain-router');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  },
};
