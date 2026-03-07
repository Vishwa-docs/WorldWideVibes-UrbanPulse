import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Layout/Header';
import Dashboard from './pages/Dashboard';
import Compare from './pages/Compare';
import StoryMode from './pages/StoryMode';
import Insights from './pages/Insights';
import Copilot from './pages/Copilot';
import BusinessModel from './pages/BusinessModel';
import { AppStateProvider, useAppState } from './context/AppStateContext';

function AppContent() {
  const { activePersona } = useAppState();

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <Header />
      <Routes>
        <Route path="/" element={<Copilot activePersona={activePersona} />} />
        <Route path="/site" element={<Dashboard activePersona={activePersona} />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/story" element={<StoryMode />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/business" element={<BusinessModel />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <AppStateProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AppStateProvider>
  );
}

export default App;
