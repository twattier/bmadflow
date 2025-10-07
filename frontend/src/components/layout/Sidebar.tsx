import { Home, FileText, MessageSquare, Settings } from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-card">
      <div className="p-6">
        <h1 className="text-2xl font-bold">BMADFlow</h1>
      </div>
      <nav className="space-y-2 p-4">
        <a href="/" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent">
          <Home className="h-5 w-5" />
          <span>Dashboard</span>
        </a>
        <a
          href="/projects"
          className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent"
        >
          <FileText className="h-5 w-5" />
          <span>Projects</span>
        </a>
        <a href="/chat" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent">
          <MessageSquare className="h-5 w-5" />
          <span>AI Chat</span>
        </a>
        <a href="/config" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent">
          <Settings className="h-5 w-5" />
          <span>Configuration</span>
        </a>
      </nav>
    </aside>
  );
}
