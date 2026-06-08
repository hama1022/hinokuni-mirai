const MAIN_SITE = 'https://hinokunimirai.com';

const SUBDOMAIN_MAP = {
  'nankan': 'nankan',
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const hostname = url.hostname;

    // www → 非wwwへ301リダイレクト
    if (hostname === 'www.hinokunimirai.com') {
      const redirectUrl = new URL(request.url);
      redirectUrl.hostname = 'hinokunimirai.com';
      return Response.redirect(redirectUrl.toString(), 301);
    }

    if (hostname === 'hinokunimirai.com') {
      return fetch(request);
    }

    const parts = hostname.split('.');
    if (parts.length < 3) return fetch(request);
    const subdomain = parts[0];

    const slug = SUBDOMAIN_MAP[subdomain];
    if (!slug) {
      return new Response('このサブドメインは登録されていません。', {
        status: 404,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      });
    }

    // ルート(/) → 団体ページ（trailing slash付きで直接アクセスしてリダイレクトを回避）
    // それ以外(/_astro/など) → メインサイトの同パス
    const targetPath = (url.pathname === '/' || url.pathname === '')
      ? `/organizations/${slug}/`
      : url.pathname + url.search;

    const targetUrl = `${MAIN_SITE}${targetPath}`;

    const response = await fetch(targetUrl);

    // content-encoding などWorkerが自動処理するヘッダーを除外して返す
    const newHeaders = new Headers();
    for (const [key, value] of response.headers.entries()) {
      const lower = key.toLowerCase();
      if (lower === 'content-encoding') continue;
      if (lower === 'transfer-encoding') continue;
      if (lower === 'content-length') continue;
      newHeaders.set(key, value);
    }

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
