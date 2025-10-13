import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { AppShell } from '@/components/layout/AppShell';
import { Dashboard } from '@/pages/Dashboard';
import { Projects } from '@/pages/Projects';
import { ProjectOverview } from '@/pages/ProjectOverview';
import { DocumentationExplorer } from '@/pages/DocumentationExplorer';
import { Chat } from '@/pages/Chat';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:projectId" element={<ProjectOverview />} />
            <Route path="/projects/:projectId/explorer" element={<DocumentationExplorer />} />
            <Route path="/projects/:projectId/chat" element={<Chat />} />
          </Routes>
        </AppShell>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
