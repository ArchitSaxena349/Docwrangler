import React, { useState, useRef } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../api';

export const UploadZone: React.FC = () => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await processUpload(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await processUpload(e.target.files[0]);
        }
    };

    const processUpload = async (file: File) => {
        setIsUploading(true);
        setStatus('idle');
        setMessage('');

        try {
            const result = await uploadDocument(file);
            setStatus('success');
            setMessage(`Uploaded: ${file.name}`);
            console.log('Upload result:', result);
        } catch (error: any) {
            setStatus('error');
            setMessage(error.message || 'Upload failed');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto mb-8">
            <div
                className={`glass-panel p-8 border-2 border-dashed transition-all cursor-pointer
          ${isDragging ? 'border-primary bg-primary/10' : 'border-gray-600 hover:border-gray-500'}
          ${status === 'error' ? 'border-red-500/50' : ''}
          ${status === 'success' ? 'border-green-500/50' : ''}
        `}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".pdf,.docx,.doc,.txt"
                />

                <div className="flex flex-col items-center gap-4 text-center">
                    {isUploading ? (
                        <Loader2 className="w-12 h-12 text-primary animate-spin" />
                    ) : status === 'success' ? (
                        <CheckCircle className="w-12 h-12 text-green-500" />
                    ) : status === 'error' ? (
                        <AlertCircle className="w-12 h-12 text-red-500" />
                    ) : (
                        <Upload className="w-12 h-12 text-gray-400" />
                    )}

                    <div>
                        <h3 className="text-lg font-semibold mb-1">
                            {isUploading ? 'Uploading...' : 'Upload Document'}
                        </h3>
                        <p className="text-sm text-gray-400">
                            {message || 'Drag & drop or click to browse'}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
