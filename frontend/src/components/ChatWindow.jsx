
import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, Sparkles } from 'lucide-react';
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

            if (response.status === 'error') {
                throw new Error(response.message || 'Unknown error from server');
            }

            // Format the response
            let botContent = `**Decision:** ${response.decision?.toUpperCase() || 'UNKNOWN'}\n\n`;
            if (response.confidence) {
                botContent += `*Confidence: ${(response.confidence * 100).toFixed(1)}%*\n\n`;
            }

            const decisionData = response.decision;

            // Handle if decision is object vs string (legacy handling)
            // But main.py now returns string for 'decision' key in root,
            // wait, check main.py response format.
            // main.py returns:
            // { "decision": "approved", "justification": "...", ... }
            // So response.decision IS the string.
            // response.justification exists.

            // Adjust to use fields from root response object if needed, 
            // OR if response matches the mock structure from before.
            // The main.py response structure:
            // { query, decision, justification, confidence, amount, source_clauses, ... }

            if (response.amount) {
                botContent += `**Approved Amount:** $${response.amount}\n\n`;
            }
            if (response.justification) {
                botContent += `${response.justification}\n\n`;
            }

            if (response.source_clauses && response.source_clauses.length > 0) {
                botContent += `**Sources:**\n${response.source_clauses.map((c) => `- ${c}`).join('\n')}`;
            }

            setMessages(prev => [...prev, { role: 'bot', content: botContent }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'bot', content: `Error: ${error.message || 'Something went wrong.'}` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[650px] w-full max-w-4xl mx-auto glass-panel overflow-hidden relative">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-50" />

            {/* Header */}
            <div className="px-6 py-4 border-b border-indigo-500/10 bg-indigo-500/5 flex items-center gap-2">
                <Sparkles size={16} className="text-indigo-400" />
                <span className="text-sm font-medium text-indigo-300">AI Assistant Active</span>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-fade-in`}
                        style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                        <div className={`
                            w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg
                            ${msg.role === 'user'
                                ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
                                : 'bg-slate-800 text-indigo-300 border border-indigo-500/20'}
                        `}>
                            {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                        </div>

                        <div className={`
                            max-w-[75%] px-5 py-3.5 text-[0.95rem] leading-relaxed shadow-md
                            ${msg.role === 'user'
                                ? 'bg-indigo-600 text-white rounded-2xl rounded-tr-sm'
                                : 'bg-slate-800/80 backdrop-blur-sm text-slate-200 rounded-2xl rounded-tl-sm border border-slate-700/50'}
                        `}>
                            <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-strong:text-indigo-200">
                                <ReactMarkdown>
                                    {msg.content}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-4 animate-pulse">
                        <div className="w-10 h-10 rounded-full bg-slate-800 border border-indigo-500/20 flex items-center justify-center">
                            <Bot size={18} className="text-indigo-300" />
                        </div>
                        <div className="bg-slate-800/50 px-5 py-3.5 rounded-2xl rounded-tl-sm border border-slate-700/50 flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                            <span className="text-sm text-slate-400">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-5 border-t border-white/5 bg-slate-900/40 backdrop-blur-md">
                <form onSubmit={handleSubmit} className="flex gap-3 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your documents..."
                        className="input pl-5 pr-14 py-3.5 bg-slate-800/50 border-slate-700/50 focus:bg-slate-800 transition-all shadow-inner text-base"
                        disabled={isLoading}
                    />
                    <div className="absolute right-2 top-1.5 bottom-1.5">
                        <button
                            type="submit"
                            className="h-full aspect-square flex items-center justify-center bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl transition-all disabled:opacity-50 disabled:hover:bg-indigo-500"
                            disabled={isLoading || !input.trim()}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
