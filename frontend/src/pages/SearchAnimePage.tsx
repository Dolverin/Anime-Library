import React, { useState } from 'react';
import { Container, Form, Button, Alert, Spinner, Toast, ToastContainer } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { animeService } from '../services/api';
import ExternalAnimeList from '../components/ExternalAnimeList';
import { ExternalAnimeSearchResult, AnimeScrapingResult } from '../types';

const SearchAnimePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ExternalAnimeSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState<Record<string, boolean>>({});
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');
  
  const navigate = useNavigate();

  // Anime auf anime-loads.org suchen
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setSearchResults([]);

    try {
      const response = await animeService.searchExternalAnime(query);
      
      if (response.error) {
        setError(`Fehler bei der Suche: ${response.error}`);
      } else if (response.data && response.data.length > 0) {
        setSearchResults(response.data);
      } else {
        setSearchResults([]);
      }
    } catch (err) {
      setError('Ein unerwarteter Fehler ist aufgetreten.');
      console.error('Suchfehler:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Einen Anime von anime-loads.org importieren
  const handleImportAnime = async (animeUrl: string) => {
    // Finde die Anime-ID aus den Suchergebnissen
    const animeToImport = searchResults.find(anime => anime.url === animeUrl);
    if (!animeToImport) return;

    // Setze den Importstatus für diesen Anime
    setIsImporting(prev => ({ ...prev, [animeToImport.id]: true }));

    try {
      // Scrape den Anime und seine Episoden
      const response = await animeService.scrapeAnimeByUrl(animeUrl);
      
      if (response.error) {
        setToastVariant('danger');
        setToastMessage(`Fehler beim Importieren: ${response.error}`);
        setShowToast(true);
        return;
      }

      const scrapingResult = response.data as AnimeScrapingResult;
      
      // Erstelle den Anime in der Datenbank
      const createResponse = await animeService.createAnime(scrapingResult.anime);
      
      if (createResponse.error) {
        setToastVariant('danger');
        setToastMessage(`Fehler beim Speichern des Animes: ${createResponse.error}`);
        setShowToast(true);
        return;
      }

      // Erfolgreicher Import
      setToastVariant('success');
      setToastMessage(`Anime "${animeToImport.title}" erfolgreich importiert!`);
      setShowToast(true);

      // Nach kurzer Verzögerung zur Detailseite navigieren
      setTimeout(() => {
        if (createResponse.data) {
          navigate(`/anime/${createResponse.data.id}`);
        }
      }, 2000);
      
    } catch (err) {
      console.error('Importfehler:', err);
      setToastVariant('danger');
      setToastMessage('Ein unerwarteter Fehler ist aufgetreten.');
      setShowToast(true);
    } finally {
      // Importstatus zurücksetzen
      setIsImporting(prev => ({ ...prev, [animeToImport.id]: false }));
    }
  };

  return (
    <Container>
      <h1 className="my-4">Anime von Anime-Loads suchen</h1>
      
      <Form onSubmit={handleSearch} className="mb-4">
        <Form.Group className="mb-3">
          <Form.Label>Suchbegriff</Form.Label>
          <div className="d-flex">
            <Form.Control 
              type="text" 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
              placeholder="z.B. One Piece, Attack on Titan, ..." 
              disabled={isSearching}
            />
            <Button 
              variant="primary" 
              type="submit" 
              disabled={isSearching || !query.trim()} 
              className="ms-2"
              style={{ minWidth: '120px' }}
            >
              {isSearching ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="me-2"
                  />
                  Suche...
                </>
              ) : (
                <>
                  <i className="bi bi-search me-2"></i>
                  Suchen
                </>
              )}
            </Button>
          </div>
          <Form.Text className="text-muted">
            Suche nach Animes auf anime-loads.org
          </Form.Text>
        </Form.Group>
      </Form>

      {error && (
        <Alert variant="danger">{error}</Alert>
      )}

      <ExternalAnimeList 
        animes={searchResults} 
        isLoading={isSearching} 
        onImportClick={handleImportAnime}
        isImporting={isImporting}
      />

      <ToastContainer position="bottom-end" className="p-3">
        <Toast 
          onClose={() => setShowToast(false)} 
          show={showToast} 
          delay={5000} 
          autohide 
          bg={toastVariant}
        >
          <Toast.Header>
            <strong className="me-auto">
              {toastVariant === 'success' ? 'Erfolg' : 'Fehler'}
            </strong>
          </Toast.Header>
          <Toast.Body className={toastVariant === 'success' ? 'text-white' : ''}>
            {toastMessage}
          </Toast.Body>
        </Toast>
      </ToastContainer>
    </Container>
  );
};

export default SearchAnimePage;
