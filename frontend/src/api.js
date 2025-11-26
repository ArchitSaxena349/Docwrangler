export const API_BASE_URL_KEY = 'docwrangler_api_url';
export const API_KEY_KEY = 'docwrangler_api_key';

export const getApiConfig = () => {
    return {
        baseUrl: import.meta.env.VITE_API_BASE_URL || localStorage.getItem(API_BASE_URL_KEY) || '',
        apiKey: localStorage.getItem(API_KEY_KEY) || '',
    };
};

export const setApiConfig = (baseUrl, apiKey) => {
    localStorage.setItem(API_BASE_URL_KEY, baseUrl);
    localStorage.setItem(API_KEY_KEY, apiKey);
};

export const sendQuery = async (query) => {
    const { baseUrl, apiKey } = getApiConfig();
    const headers = {
        'Content-Type': 'application/json',
    };

    if (apiKey) {
        headers['x-api-key'] = apiKey;
    }

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

export const uploadDocument = async (file) => {
    const { baseUrl, apiKey } = getApiConfig();
    const headers = {};

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
