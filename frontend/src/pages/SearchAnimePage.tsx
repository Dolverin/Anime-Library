import React, { useState } from 'react';
import { Container, Form, Button, Alert, Spinner, Toast, ToastContainer, Row, Col, Card, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { animeService } from '../services/api';
import ExternalAnimeList from '../components/ExternalAnimeList';
import { ExternalAnimeSearchResult, AnimeScrapingResult } from '../types';

interface DbAnimeResult {
  id: number;
  titel_de: string;
  titel_jp?: string;
  titel_en?: string;
  titel_org?: string;
  synonyme?: string;
  anime_loads_id?: string;
  anime_loads_url?: string;
  cover_image_url?: string;
  updated_at: Date;
  episodes_count: number;
  latest_episode_update?: Date;
}

interface CombinedSearchResult {
  db_results: DbAnimeResult[];
  external_results: Array<{
    id: string;
    title: string;
    url: string;
    image_url?: string;
    in_database?: boolean;
    db_id?: number;
    updated_at?: Date;
  }>;
}

const SearchAnimePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [dbResults, setDbResults] = useState<DbAnimeResult[]>([]);
  const [externalResults, setExternalResults] = useState<ExternalAnimeSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState<Record<string, boolean>>({});
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastVariant, setToastVariant] = useState<'success' | 'danger'>('success');
  
  const navigate = useNavigate();

  // Kombinierte Suche in der Datenbank und auf anime-loads.org 
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setDbResults([]);
    setExternalResults([]);

    try {
      const response = await animeService.combinedSearch(query);
      
      if (response.error) {
        setError(`Fehler bei der Suche: ${response.error}`);
      } else if (response.data) {
        const combinedData = response.data as CombinedSearchResult;
        setDbResults(combinedData.db_results || []);
        setExternalResults(combinedData.external_results || []);
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
    const animeToImport = externalResults.find(anime => anime.url === animeUrl);
    if (!animeToImport) return;

    // Prüfen, ob der Anime bereits in der Datenbank ist
    if (animeToImport.in_database && animeToImport.db_id) {
      setToastVariant('success');
      setToastMessage(`Anime "${animeToImport.title}" ist bereits in deiner Bibliothek!`);
      setShowToast(true);
      
      // Nach kurzer Verzögerung zur Detailseite navigieren
      setTimeout(() => {
        navigate(`/anime/${animeToImport.db_id}`);
      }, 1500);
      return;
    }

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

  // Formatiert das Datum für die Anzeige
  const formatDate = (dateString?: Date) => {
    if (!dateString) return "Unbekannt";
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Container>
      <h1 className="my-4">Anime suchen</h1>
      
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
            Suche nach Anime in deiner Datenbank und auf anime-loads.org
          </Form.Text>
        </Form.Group>
      </Form>

      {error && (
        <Alert variant="danger">{error}</Alert>
      )}

      {/* Ergebnisse aus der Datenbank */}
      {dbResults.length > 0 && (
        <div className="mb-5">
          <h2 className="mb-3">In deiner Bibliothek gefunden</h2>
          <Row xs={1} md={2} lg={3} className="g-4">
            {dbResults.map(anime => (
              <Col key={anime.id}>
                <Card className="h-100">
                  {anime.cover_image_url && (
                    <Card.Img 
                      variant="top" 
                      src={anime.cover_image_url} 
                      alt={anime.titel_de}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                  )}
                  <Card.Body>
                    <Card.Title>{anime.titel_de}</Card.Title>
                    {anime.titel_jp && <Card.Subtitle className="mb-2 text-muted">{anime.titel_jp}</Card.Subtitle>}
                    <div className="mt-3">
                      <Badge bg="info" className="me-2">
                        {anime.episodes_count} Episoden
                      </Badge>
                      <small className="text-muted d-block mt-2">
                        Aktualisiert: {formatDate(anime.updated_at)}
                      </small>
                    </div>
                    <div className="d-grid mt-3">
                      <Button 
                        variant="primary" 
                        onClick={() => navigate(`/anime/${anime.id}`)}
                      >
                        Details anzeigen
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* Externe Suchergebnisse */}
      <div className="mt-4">
        <h2 className="mb-3">Auf anime-loads.org gefunden</h2>
        <ExternalAnimeList 
          animes={externalResults} 
          isLoading={isSearching} 
          onImportClick={handleImportAnime}
          isImporting={isImporting}
        />
      </div>

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
