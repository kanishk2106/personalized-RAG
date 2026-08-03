import { GoogleAuth } from "google-auth-library";
import { RAG_SERVICE_URL } from "../config.js";
const auth = new GoogleAuth();
let cachedClient = null;
export async function getIdToken() {
    if (!cachedClient) {
        cachedClient = await auth.getIdTokenClient(RAG_SERVICE_URL);
    }
    const headers = await cachedClient.getRequestHeaders();
    return headers.Authorization.replace("Bearer ", "");
}
//# sourceMappingURL=auth.js.map