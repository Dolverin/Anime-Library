import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import 'bootstrap/dist/css/bootstrap.min.css'
import './App.css'

// Komponenten importieren
import NavBar from './components/NavBar'
import HomePage from './pages/HomePage'
import AnimeDetailPage from './pages/AnimeDetailPage'
import SearchPage from './pages/SearchPage'

function App() {
  return (
    <Router>
      <div className="app-container">
        <NavBar />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/anime/:id" element={<AnimeDetailPage />} />
            <Route path="/suche" element={<SearchPage />} />
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
