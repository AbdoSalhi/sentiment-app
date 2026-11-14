export async function predire(baseUrl, key, text, fetcher = fetch) {
  const response = await fetcher(`${baseUrl.replace(/\/$/, '')}/v1/predict`, {
    method: 'POST', headers: {'Content-Type': 'application/json', 'X-API-Key': key},
    body: JSON.stringify({text})
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.erreur?.message || 'Réponse du service invalide');
  if (!['POSITIVE', 'NEGATIVE', 'INDETERMINE'].includes(result.label) ||
      typeof result.score !== 'number' || !Number.isFinite(result.score) ||
      result.score < 0 || result.score > 1) throw new Error('Réponse du service invalide');
  return result;
}
