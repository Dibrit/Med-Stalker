export type DrfErrorPayload =
  | { detail: string }
  | Record<string, string[]>
  | unknown;

export function isDetailError(payload: DrfErrorPayload): payload is { detail: string } {
  return !!payload && typeof payload === 'object' && 'detail' in (payload as any) && typeof (payload as any).detail === 'string';
}

export function fieldErrors(payload: DrfErrorPayload): Record<string, string[]> {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return {};
  if (isDetailError(payload)) return {};
  const rec = payload as Record<string, unknown>;
  const out: Record<string, string[]> = {};
  for (const [k, v] of Object.entries(rec)) {
    if (Array.isArray(v) && v.every((x) => typeof x === 'string')) out[k] = v as string[];
  }
  return out;
}

export function summarizeError(payload: DrfErrorPayload): string {
  if (isDetailError(payload)) return payload.detail;
  const fields = fieldErrors(payload);
  const first = Object.values(fields)[0]?.[0];
  return first ?? 'Request failed.';
}

