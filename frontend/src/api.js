const API_BASE = "/api";


async function request(url, options = {}) {

  const response = await fetch(
    `${API_BASE}${url}`,
    {
      ...options,

      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    }
  );


  if (!response.ok) {

    let message = `API error ${response.status}`;

    try {

      const data = await response.json();

      if (data?.detail) {
        message = data.detail;
      }

    } catch {

      try {

        const text = await response.text();

        if (text) {
          message = text;
        }

      } catch {
        // Ignore parsing errors
      }
    }

    throw new Error(message);
  }


  return response.json();
}


/*
 * Patienten
 */
export async function getPatients() {

  return request(
    "/patients/"
  );
}


/*
 * Fälle
 */
export async function getCases() {

  return request(
    "/cases/"
  );
}


/*
 * Einzelnen Fall analysieren
 */
export async function analyzeCase(caseId) {

  if (!caseId) {
    throw new Error(
      "Keine Case-ID angegeben."
    );
  }

  return request(
    `/agents/analyze/${caseId}`
  );
}


/*
 * Medizinische Dokumente
 */
export async function getDocuments() {

  return request(
    "/documents/"
  );
}


/*
 * RAG-Suche
 */
export async function searchRag(
  query,
  caseId = null,
  limit = 3
) {

  if (!query?.trim()) {

    throw new Error(
      "Die RAG-Suche benötigt eine Suchanfrage."
    );
  }


  const params =
    new URLSearchParams();

  params.set(
    "q",
    query
  );

  if (caseId) {

    params.set(
      "case_id",
      caseId
    );
  }

  params.set(
    "limit",
    limit
  );


  return request(
    `/rag/search?${params.toString()}`
  );
}

