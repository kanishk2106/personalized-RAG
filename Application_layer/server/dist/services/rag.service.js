import { RAG_SERVICE_URL } from "../config.js";
import { getIdToken } from "../helpers/auth.js";
/** Forward a chat request to the upstream RAG service (returns the raw streaming response). */
export async function forwardChat(body) {
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
/** Forward a retrieve request to the upstream RAG service. */
export async function forwardRetrieve(body) {
    const token = await getIdToken();
    return fetch(`${RAG_SERVICE_URL}/retrieve`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
}
/** Probe the upstream RAG service health. */
export async function forwardHealth() {
    const token = await getIdToken();
    return fetch(`${RAG_SERVICE_URL}/health`, {
        headers: { Authorization: `Bearer ${token}` },
    });
}
//# sourceMappingURL=rag.service.js.map