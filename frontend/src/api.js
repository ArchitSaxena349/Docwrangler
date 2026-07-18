export const getApiConfig = () => {
    return {
        // Fallback to empty string so requests automatically route to relative path of hosting server
        baseUrl: import.meta.env.VITE_API_BASE_URL || '',
        apiKey: import.meta.env.VITE_API_KEY || '',
    };
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

export const getTaskStatus = async (documentId) => {
    const { baseUrl, apiKey } = getApiConfig();
    const headers = {};

    if (apiKey) {
        headers['x-api-key'] = apiKey;
    }

    const response = await fetch(`${baseUrl}/api/tasks/${documentId}`, {
        method: 'GET',
        headers,
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch task status: ${response.statusText}`);
    }

    return response.json();
};
