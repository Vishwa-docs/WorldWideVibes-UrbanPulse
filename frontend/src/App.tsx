import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Layout/Header';
import Dashboard from './pages/Dashboard';
import Compare from './pages/Compare';
import StoryMode from './pages/StoryMode';
import { usePersona } from './hooks/usePersona';

function App() {
  const { activePersona, togglePersona } = usePersona();

  return (
    <BrowserRouter>
      <div className="h-screen flex flex-col bg-gray-100">
        <Header activePersona={activePersona} onTogglePersona={togglePersona} />
        <Routes>
          <Route path="/" element={<Dashboard activePersona={activePersona} />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/story" element={<StoryMode />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
