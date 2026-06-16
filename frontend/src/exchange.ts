const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function encryptApiKey(key: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const material = await crypto.subtle.importKey(
    'raw',
    encoder.encode(import.meta.env.VITE_EXCHANGE_KEY || 'jarvistrader-exchange-key-32bytes!!!!!!'),
    { name: 'AES-GCM' },
    false,
    ['encrypt']
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    material,
    encoder.encode(`${key}:${secret}`)
  );
  const combined = new Uint8Array(iv.length + new Uint8Array(ciphertext).length);
  combined.set(iv);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return btoa(String.fromCharCode(...combined));
}

export async function decryptApiKey(blob: string): Promise<{ key: string; secret: string }> {
  try {
    const raw = Uint8Array.from(atob(blob), c => c.charCodeAt(0));
    const iv = raw.slice(0, 12);
    const data = raw.slice(12);
    const material = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(import.meta.env.VITE_EXCHANGE_KEY || 'jarvistrader-exchange-key-32bytes!!!!!!'),
      { name: 'AES-GCM' },
      false,
      ['decrypt']
    );
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, material, data);
    const decoded = new TextDecoder().decode(plain);
    const [key, secret] = decoded.split(':');
    return { key, secret };
  } catch (e) {
    console.error('decrypt failed', e);
    return { key: '', secret: '' };
  }
}

export async function createExchangeSession(encryptedBlob: string) {
  const { key, secret } = await decryptApiKey(encryptedBlob);
  if (!key || !secret) return null;
  const res = await fetch(`${API_URL}/api/exchange/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ encrypted_blob: encryptedBlob, exchange: 'binance' }),
  });
  if (!res.ok) throw new Error('Failed to create exchange session');
  return res.json();
}
