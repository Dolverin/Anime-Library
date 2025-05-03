import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import 'bootstrap/dist/css/bootstrap.min.css'
import './App.css'

// Komponenten importieren
import NavBar from './components/NavBar'
import HomePage from './pages/HomePage'
import AnimeDetailPage from './pages/AnimeDetailPage'
import SearchPage from './pages/SearchPage'
import MyAnimes from './pages/MyAnimes'
import AvailableAnimes from './pages/AvailableAnimes'
import AddAnimePage from './pages/AddAnimePage'
import EditAnimePage from './pages/EditAnimePage'
import AddEpisodePage from './pages/AddEpisodePage'
import EditEpisodePage from './pages/EditEpisodePage'

function App() {
  return (
    <Router>
      <div className="app-container">
        <NavBar />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/anime/:id" element={<AnimeDetailPage />} />
            <Route path="/anime/:id/bearbeiten" element={<EditAnimePage />} />
            <Route path="/anime/:animeId/episode/hinzufuegen" element={<AddEpisodePage />} />
            <Route path="/anime/:animeId/episode/:episodeId/bearbeiten" element={<EditEpisodePage />} />
            <Route path="/suche" element={<SearchPage />} />
            <Route path="/meine-animes" element={<MyAnimes />} />
            <Route path="/verfügbar" element={<AvailableAnimes />} />
            <Route path="/anime-hinzufuegen" element={<AddAnimePage />} />
            <Route path="*" element={<div className="container mt-5 text-center"><h2>404 - Seite nicht gefunden</h2></div>} />
          </Routes>
        </main>
        <footer className="text-center py-4 mt-5 border-top">
          <div className="container">
            <p className="mb-0 text-muted">Anime Bibliothek &copy; {new Date().getFullYear()}</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
