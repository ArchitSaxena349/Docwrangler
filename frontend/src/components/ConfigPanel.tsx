import React, { useState, useEffect } from 'react';
import { Settings, Save } from 'lucide-react';
import { getApiConfig, setApiConfig } from '../api';

export const ConfigPanel: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [baseUrl, setBaseUrl] = useState('');
    const [apiKey, setApiKey] = useState('');

    useEffect(() => {
        const config = getApiConfig();
        setBaseUrl(config.baseUrl);
        setApiKey(config.apiKey);
    }, []);

    const handleSave = () => {
        setApiConfig(baseUrl, apiKey);
        setIsOpen(false);
        window.location.reload(); // Reload to apply changes
    };

    return (
        <div className="fixed top-4 right-4 z-50">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="btn btn-ghost p-2 rounded-full hover:bg-white/10"
            >
                <Settings size={24} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 glass-panel p-4 text-left animate-in fade-in slide-in-from-top-2">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Settings size={18} /> API Configuration
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1 text-gray-300">API Base URL</label>
                            <input
                                type="text"
                                value={baseUrl}
                                onChange={(e) => setBaseUrl(e.target.value)}
                                className="input"
                                placeholder="http://localhost:8000"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1 text-gray-300">API Key (Optional)</label>
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                className="input"
                                placeholder="Secret Key"
                            />
                        </div>

                        <button onClick={handleSave} className="btn btn-primary w-full">
                            <Save size={16} /> Save & Reload
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
