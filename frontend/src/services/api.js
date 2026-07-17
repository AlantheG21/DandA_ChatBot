const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function sendMessage(query) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const data = await response.json();
  return data.response;
}
