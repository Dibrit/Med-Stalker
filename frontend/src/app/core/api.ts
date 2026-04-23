export function apiBaseUrl(): string {
  // Prefer 127.0.0.1 per backend docs, but handle localhost smoothly.
  const host = globalThis.location?.hostname;
  if (host === 'localhost') return 'http://localhost:8000/api/';
  return 'http://127.0.0.1:8000/api/';
}

export function apiUrl(path: string): string {
  const base = apiBaseUrl();
  if (!path) return base;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return base + path.replace(/^\//, '');
}

