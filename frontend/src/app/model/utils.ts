
export class HttpUtils {
  public static toGetUrl(url: string, params?: Record<string, any>): string {
    const query = new URLSearchParams(params || {}).toString();
    if (!query) return url;
    return url.includes('?') ? `${url}&${query}` : `${url}?${query}`;
  }

  public static translateObjToForm(obj: Record<string, any>): string {
    return Object.entries(obj)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join('&');
  }
}