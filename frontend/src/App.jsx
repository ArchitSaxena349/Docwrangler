import { UploadZone } from './components/UploadZone';
import { ChatWindow } from './components/ChatWindow';
import { ShieldCheck } from 'lucide-react';

function App() {
    return (
        <div className="min-h-screen pb-20 relative">
            {/* Ambient Background decoration */}
            <div className="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-indigo-900/20 to-transparent pointer-events-none -z-10" />

            <header className="pt-20 pb-12 text-center relative z-10">
                <div className="flex items-center justify-center gap-4 mb-6">
                    <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 shadow-lg backdrop-blur-sm">
                        <ShieldCheck size={36} className="text-indigo-400" />
                    </div>
                    <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-indigo-400 drop-shadow-sm">
                        DocWrangler
                    </h1>
                </div>
                <p className="text-slate-400 text-lg max-w-xl mx-auto leading-relaxed font-light">
                    Intelligent insurance document processing
                </p>
            </header>

            <main className="container mx-auto px-4 max-w-5xl space-y-8 relative z-10">
                <section className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
                    <UploadZone />
                </section>

                <section className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <ChatWindow />
                </section>
            </main>
        </div>
    );
}

export default App;
