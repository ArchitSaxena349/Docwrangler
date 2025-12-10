
import { useState, useRef } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2, FileText } from 'lucide-react';
import { uploadDocument } from '../api';

export const UploadZone = () => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [status, setStatus] = useState('idle');
    const [message, setMessage] = useState('');
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await processUpload(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = async (e) => {
        if (e.target.files && e.target.files[0]) {
            await processUpload(e.target.files[0]);
        }
    };

    const processUpload = async (file) => {
        setIsUploading(true);
        setStatus('idle');
        setMessage('');

        try {
            const result = await uploadDocument(file);
            setStatus('success');
            setMessage(`Successfully indexed: ${file.name}`);
            console.log('Upload result:', result);
        } catch (error) {
            setStatus('error');
            setMessage(error.message || 'Upload failed');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto mb-8">
            <div
                className={`
                    relative group transition-all duration-300 ease-out cursor-pointer overflow-hidden
                    glass-panel p-10 border-2 border-dashed
                    ${isDragging
                        ? 'border-indigo-400 bg-indigo-500/10 scale-[1.02]'
                        : 'border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/30'}
                    ${status === 'error' ? 'border-red-500/50 bg-red-500/5' : ''}
                    ${status === 'success' ? 'border-emerald-500/50 bg-emerald-500/5' : ''}
                `}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".pdf,.docx,.doc,.txt"
                />

                <div className="relative flex flex-col items-center gap-5 text-center z-10">
                    <div className={`
                        w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-xl
                        ${isUploading ? 'bg-indigo-500/20' :
                            status === 'success' ? 'bg-emerald-500/20' :
                                status === 'error' ? 'bg-red-500/20' :
                                    'bg-slate-800 border border-slate-700 group-hover:scale-110 group-hover:border-indigo-500/30'}
                    `}>
                        {isUploading ? (
                            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                        ) : status === 'success' ? (
                            <CheckCircle className="w-8 h-8 text-emerald-400" />
                        ) : status === 'error' ? (
                            <AlertCircle className="w-8 h-8 text-red-400" />
                        ) : (
                            <Upload className="w-8 h-8 text-indigo-400" />
                        )}
                    </div>

                    <div className="space-y-2">
                        <h3 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-white">
                            {isUploading ? 'Processing Document...' : 'Upload Policy Document'}
                        </h3>
                        <p className="text-slate-400 max-w-sm mx-auto leading-relaxed">
                            {message || (
                                <>
                                    <span className="text-indigo-300 font-medium">Drag & drop</span> or click to browse
                                    <br />
                                    <span className="text-xs opacity-60 mt-2 block">Supports PDF, DOCX, TXT</span>
                                </>
                            )}
                        </p>
                    </div>

                    {status === 'success' && (
                        <div className="mt-2 text-xs font-mono text-emerald-400/80 bg-emerald-950/30 px-3 py-1 rounded-full border border-emerald-500/20">
                            Ready for Querying
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
