import { RAG_SERVICE_URL } from "../config.js";
import { getIdToken } from "../helpers/auth.js";


/** Forward a chat request to the upstream RAG service (returns the raw streaming response). */
export async function forwardChat(body: unknown): Promise<Response> {
  const token = await getIdToken();
  return fetch(`${RAG_SERVICE_URL}/chat`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}
