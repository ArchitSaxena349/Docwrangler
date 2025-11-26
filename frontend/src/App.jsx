import { ConfigPanel } from './components/ConfigPanel';
import { UploadZone } from './components/UploadZone';
import { ChatWindow } from './components/ChatWindow';
import { ShieldCheck } from 'lucide-react';

function App() {
    return (
        <div className="min-h-screen pb-12">
            <ConfigPanel />

            <header className="mb-12 pt-12">
                <div className="flex items-center justify-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center text-primary">
                        <ShieldCheck size={32} />
                    </div>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
                        DocWrangler
                    </h1>
                </div>
                <p className="text-gray-400 text-lg max-w-lg mx-auto">
                    Intelligent insurance document processing powered by Gemini AI.
                </p>
            </header>

            <main className="container mx-auto px-4 space-y-8">
                <section>
                    <UploadZone />
                </section>

                <section>
                    <ChatWindow />
                </section>
            </main>
        </div>
    );
}

export default App;
