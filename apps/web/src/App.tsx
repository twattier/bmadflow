import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/layout/Header';
import TabNavigation from './components/layout/TabNavigation';
import ScopingView from './pages/ScopingView';
import ArchitectureView from './pages/ArchitectureView';
import EpicsView from './pages/EpicsView';
import DetailView from './pages/DetailView';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <Header />
        <TabNavigation />
        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/scoping" replace />} />
            <Route path="/scoping" element={<ScopingView />} />
            <Route path="/architecture" element={<ArchitectureView />} />
            <Route path="/epics" element={<EpicsView />} />
            <Route path="/detail" element={<DetailView />} />
            <Route path="/detail/:documentId" element={<DetailView />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
