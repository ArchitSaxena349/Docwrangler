import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendQuery } from '../api';

export const ChatWindow = () => {
    const [messages, setMessages] = useState([
        { role: 'bot', content: 'Hello! I can help you answer questions about your insurance documents. Upload a policy or claim document to get started.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await sendQuery(userMessage);

            // Format the response
            let botContent = `**Decision:** ${response.decision.toUpperCase()}\n\n`;
            if (response.confidence) {
                botContent += `*Confidence: ${(response.confidence * 100).toFixed(1)}%*\n\n`;
            }

            const decisionData = response.decision;

            if (typeof decisionData === 'object') {
                botContent = `**Decision:** ${decisionData.decision?.toUpperCase() || 'UNKNOWN'}\n\n`;
                if (decisionData.amount) {
                    botContent += `**Approved Amount:** $${decisionData.amount}\n\n`;
                }
                botContent += `${decisionData.justification}\n\n`;

                if (decisionData.source_clauses && decisionData.source_clauses.length > 0) {
                    botContent += `**Sources:**\n${decisionData.source_clauses.map((c) => `- ${c}`).join('\n')}`;
                }
            } else {
                // Fallback if it's just a string
                botContent += String(decisionData);
            }

            setMessages(prev => [...prev, { role: 'bot', content: botContent }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'bot', content: `Error: ${error.message || 'Something went wrong.'}` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[600px] w-full max-w-4xl mx-auto glass-panel overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                        <div className={`
              w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
              ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-gray-700 text-gray-300'}
            `}>
                            {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>

                        <div className={`
              max-w-[80%] rounded-2xl px-4 py-2 text-sm text-left
              ${msg.role === 'user'
                                ? 'bg-primary text-white rounded-tr-none'
                                : 'bg-gray-800/50 text-gray-200 rounded-tl-none border border-gray-700/50'}
            `}>
                            <div className="prose prose-invert prose-sm max-w-none">
                                <ReactMarkdown>
                                    {msg.content}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                            <Bot size={16} className="text-gray-300" />
                        </div>
                        <div className="bg-gray-800/50 rounded-2xl rounded-tl-none px-4 py-2 border border-gray-700/50 flex items-center">
                            <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-700/30 bg-gray-900/30">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your documents..."
                        className="input flex-1"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary px-4"
                        disabled={isLoading || !input.trim()}
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};
