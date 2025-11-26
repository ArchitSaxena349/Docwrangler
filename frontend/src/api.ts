export const API_BASE_URL_KEY = 'docwrangler_api_url';
export const API_KEY_KEY = 'docwrangler_api_key';

export const getApiConfig = () => {
    return {
        baseUrl: localStorage.getItem(API_BASE_URL_KEY) || '',
        apiKey: localStorage.getItem(API_KEY_KEY) || '',
    };
};

export const setApiConfig = (baseUrl: string, apiKey: string) => {
    localStorage.setItem(API_BASE_URL_KEY, baseUrl);
    localStorage.setItem(API_KEY_KEY, apiKey);
};

export interface ChatResponse {
    query: string;
    decision: string;
    confidence: number;
    parsed_query: any;
    retrieved_documents: any[];
}

export const sendQuery = async (query: string): Promise<ChatResponse> => {
    const { baseUrl, apiKey } = getApiConfig();
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };

    if (apiKey) {
        headers['x-api-key'] = apiKey;
    }

    // Try /api/query first (protected), fall back to /webhook/query if 404 or 403 (maybe)
    // Actually, let's just use /webhook/query for simplicity as it's backward compatible
    // But the plan said "Integrate with Backend API".
    // Let's use /webhook/query as it's the main one we tested.
    // Wait, /webhook/query doesn't require auth unless we added it?
    // We added auth to /api/* routes. /webhook/* are backward compatible.
    // But for a "premium" app we should probably use the secure routes if available.
    // However, the user might not have set APP_API_KEY.
    // Let's use /webhook/query for now to ensure it works out of the box.

    const response = await fetch(`${baseUrl}/webhook/query`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
};

export const uploadDocument = async (file: File) => {
    const { baseUrl, apiKey } = getApiConfig();
    const headers: HeadersInit = {};

    if (apiKey) {
        headers['x-api-key'] = apiKey;
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${baseUrl}/api/upload`, {
        method: 'POST',
        headers,
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Upload Failed: ${response.statusText}`);
    }

    return response.json();
};
