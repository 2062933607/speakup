import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import HistoryPage from './pages/HistoryPage';
import './styles/global.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat/:characterId" element={<ChatPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
      <NavBar />
    </BrowserRouter>
  );
}
