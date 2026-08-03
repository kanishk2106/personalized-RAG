import { GoogleAuth } from "google-auth-library";
import { RAG_SERVICE_URL } from "../config.js";


const auth = new GoogleAuth();

let cachedClient: Awaited<ReturnType<GoogleAuth["getIdTokenClient"]>> | null =
  null;


export async function getIdToken(): Promise<string> {
  if (!cachedClient) {
    cachedClient = await auth.getIdTokenClient(RAG_SERVICE_URL);
  }
  const headers = await cachedClient.getRequestHeaders();
  return headers.Authorization!.replace("Bearer ", "");
}
