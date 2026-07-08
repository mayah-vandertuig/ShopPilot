export function normalizeEtsyShopInput(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";

  const urlMatch = trimmed.match(/etsy\.com\/shop\/([^/?#]+)/i);
  if (urlMatch) return decodeURIComponent(urlMatch[1]);

  if (trimmed.startsWith("@")) return trimmed.slice(1).trim();

  return trimmed;
}
