import { useState, useEffect } from 'react';
import { Container, Row, Col, Spinner, Alert, Form, ToggleButton, Button, Card, Badge, InputGroup, Tabs, Tab, ProgressBar } from 'react-bootstrap';
import { Anime, Episode, EpisodeAvailabilityStatus, ExternalAnimeSearchResult, AnimeScrapingResult } from '../types';
import { animeService, episodeService } from '../services/api';
import { FaSearch, FaExternalLinkAlt, FaDownload, FaExclamationTriangle, FaSync, FaCheck, FaArrowRight } from 'react-icons/fa';

const AvailableAnimes = () => {
  const [animes, setAnimes] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [availabilityFilter, setAvailabilityFilter] = useState<string>('all');
  const [animeWithEpisodes, setAnimeWithEpisodes] = useState<Map<number, Episode[]>>(new Map());
  
  // Für die externe Suche
  const [externalSearchQuery, setExternalSearchQuery] = useState<string>('');
  const [externalSearchResults, setExternalSearchResults] = useState<ExternalAnimeSearchResult[]>([]);
  const [externalSearchLoading, setExternalSearchLoading] = useState<boolean>(false);
  const [externalSearchError, setExternalSearchError] = useState<string | null>(null);
  
  // Für die Scraping-Funktionalität
  const [scrapingResult, setScrapingResult] = useState<AnimeScrapingResult | null>(null);
  const [scrapingLoading, setScrapingLoading] = useState<boolean>(false);
  const [scrapingError, setScrapingError] = useState<string | null>(null);
  const [importingAnime, setImportingAnime] = useState<boolean>(false);
  const [importSuccess, setImportSuccess] = useState<boolean>(false);
  
  // Tab-Steuerung
  const [activeTab, setActiveTab] = useState<string>('browse');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Alle Animes abrufen
        const animesResponse = await animeService.getAllAnimes();
        
        if (animesResponse.error) {
          setError(animesResponse.error);
          setLoading(false);
          return;
        }
        
        const allAnimes = animesResponse.data?.items || [];
        setAnimes(allAnimes);
        
        // Für jeden Anime die Episoden laden
        const episodesMap = new Map<number, Episode[]>();
        
        for (const anime of allAnimes) {
          const episodesResponse = await episodeService.getEpisodesByAnimeId(anime.id);
          if (episodesResponse.data) {
            episodesMap.set(anime.id, episodesResponse.data);
          }
        }
        
        setAnimeWithEpisodes(episodesMap);
      } catch (err) {
        setError('Ein Fehler ist beim Laden der Daten aufgetreten.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Externe Suche nach Anime auf anime-loads.org
  const handleExternalSearch = async () => {
    if (!externalSearchQuery.trim()) return;
    
    setExternalSearchLoading(true);
    setExternalSearchError(null);
    setExternalSearchResults([]);
    
    try {
      const response = await animeService.searchExternalAnime(externalSearchQuery);
      
      if (response.error) {
        setExternalSearchError(response.error);
      } else if (response.data) {
        setExternalSearchResults(response.data);
      }
    } catch (err) {
      setExternalSearchError('Ein Fehler ist bei der externen Suche aufgetreten.');
      console.error(err);
    } finally {
      setExternalSearchLoading(false);
    }
  };

  // Anime von anime-loads.org scrapen
  const handleScrapeAnime = async (url: string) => {
    setScrapingLoading(true);
    setScrapingError(null);
    setScrapingResult(null);
    setImportSuccess(false);
    
    try {
      const response = await animeService.scrapeAnimeByUrl(url);
      
      if (response.error) {
        setScrapingError(response.error);
      } else if (response.data) {
        setScrapingResult(response.data);
      }
    } catch (err) {
      setScrapingError('Ein Fehler ist beim Scraping des Animes aufgetreten.');
      console.error(err);
    } finally {
      setScrapingLoading(false);
    }
  };

  // Gescrapten Anime importieren
  const handleImportAnime = async () => {
    if (!scrapingResult) return;
    
    setImportingAnime(true);
    
    try {
      // Erstelle den Anime
      const animeResponse = await animeService.createAnime(scrapingResult.anime);
      
      if (animeResponse.error) {
        setScrapingError(`Fehler beim Erstellen des Animes: ${animeResponse.error}`);
        setImportingAnime(false);
        return;
      }
      
      if (!animeResponse.data) {
        setScrapingError('Keine Daten vom Server erhalten.');
        setImportingAnime(false);
        return;
      }
      
      const newAnimeId = animeResponse.data.id;
      
      // Erstelle alle Episoden
      for (const episode of scrapingResult.episodes) {
        // Stelle sicher, dass die Episode mit der korrekten Anime-ID erstellt wird
        const episodeData = {
          ...episode,
          anime_id: newAnimeId
        };
        
        await episodeService.createEpisode(newAnimeId, episodeData);
      }
      
      // Aktualisiere die Anzeige
      const updatedAnimes = [...animes, animeResponse.data];
      setAnimes(updatedAnimes);
      
      // Hole die frisch erstellten Episoden
      const episodesResponse = await episodeService.getEpisodesByAnimeId(newAnimeId);
      if (episodesResponse.data) {
        const updatedEpisodesMap = new Map(animeWithEpisodes);
        updatedEpisodesMap.set(newAnimeId, episodesResponse.data);
        setAnimeWithEpisodes(updatedEpisodesMap);
      }
      
      // Zeige Erfolg an
      setImportSuccess(true);
      
      // Wechsle zum Browse-Tab, damit der Benutzer den neuen Anime sehen kann
      setActiveTab('browse');
    } catch (err) {
      setScrapingError('Ein Fehler ist beim Importieren des Animes aufgetreten.');
      console.error(err);
    } finally {
      setImportingAnime(false);
    }
  };

  // Prüft, ob ein Anime bereits in der lokalen Datenbank existiert
  const isAnimeInDatabase = (title: string): boolean => {
    return animes.some(anime => 
      anime.titel_de.toLowerCase() === title.toLowerCase() ||
      (anime.titel_jp && anime.titel_jp.toLowerCase() === title.toLowerCase()) ||
      (anime.titel_en && anime.titel_en.toLowerCase() === title.toLowerCase())
    );
  };

  // Filtert Animes basierend auf der Verfügbarkeit ihrer Episoden
  const filteredAnimes = animes.filter(anime => {
    const episodes = animeWithEpisodes.get(anime.id) || [];
    
    if (availabilityFilter === 'all') {
      return true;
    }
    
    if (availabilityFilter === 'online') {
      return episodes.some(
        ep => ep.availability_status === EpisodeAvailabilityStatus.AVAILABLE_ONLINE || 
              ep.availability_status === EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE
      );
    }
    
    if (availabilityFilter === 'local') {
      return episodes.some(
        ep => ep.availability_status === EpisodeAvailabilityStatus.OWNED || 
              ep.availability_status === EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE
      );
    }
    
    return false;
  });

  // Verfügbarkeitsstatus berechnen
  const calculateAvailability = (animeId: number): { totalEpisodes: number, onlineCount: number, localCount: number } => {
    const episodes = animeWithEpisodes.get(animeId) || [];
    const totalEpisodes = episodes.length;
    const onlineCount = episodes.filter(ep => 
      ep.availability_status === EpisodeAvailabilityStatus.AVAILABLE_ONLINE || 
      ep.availability_status === EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE
    ).length;
    const localCount = episodes.filter(ep => 
      ep.availability_status === EpisodeAvailabilityStatus.OWNED || 
      ep.availability_status === EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE
    ).length;
    
    return { totalEpisodes, onlineCount, localCount };
  };

  return (
    <Container>
      <h1 className="mb-4">Anime-Verfügbarkeit & Import</h1>

      <Tabs 
        activeKey={activeTab} 
        onSelect={(k) => setActiveTab(k || 'browse')}
        className="mb-4"
      >
        <Tab eventKey="browse" title="Meine verfügbaren Animes">
          {/* Verfügbarkeits-Filter */}
          <Form.Group className="mb-4">
            <Form.Label>Verfügbarkeit:</Form.Label>
            <div className="d-flex gap-2">
              <ToggleButton
                id="toggle-all"
                type="radio"
                variant="outline-primary"
                name="availability"
                value="all"
                checked={availabilityFilter === 'all'}
                onChange={(e) => setAvailabilityFilter(e.currentTarget.value)}
              >
                Alle anzeigen
              </ToggleButton>
              <ToggleButton
                id="toggle-online"
                type="radio"
                variant="outline-info"
                name="availability"
                value="online"
                checked={availabilityFilter === 'online'}
                onChange={(e) => setAvailabilityFilter(e.currentTarget.value)}
              >
                Online verfügbar
              </ToggleButton>
              <ToggleButton
                id="toggle-local"
                type="radio"
                variant="outline-success"
                name="availability"
                value="local"
                checked={availabilityFilter === 'local'}
                onChange={(e) => setAvailabilityFilter(e.currentTarget.value)}
              >
                Lokal verfügbar
              </ToggleButton>
            </div>
          </Form.Group>

          {/* Lade-Indikator */}
          {loading && (
            <div className="text-center my-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2">Lade verfügbare Animes...</p>
            </div>
          )}

          {/* Fehlermeldung */}
          {error && (
            <Alert variant="danger">
              Fehler beim Laden der Daten: {error}
            </Alert>
          )}

          {/* Keine Anime-Nachricht */}
          {!loading && !error && filteredAnimes.length === 0 && (
            <Alert variant="info">
              Keine verfügbaren Animes gefunden für die ausgewählten Filter.
            </Alert>
          )}

          {/* Anime-Karten-Grid mit Verfügbarkeitsinfo */}
          {!loading && !error && filteredAnimes.length > 0 && (
            <>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <p className="mb-0">{filteredAnimes.length} verfügbare Anime(s) gefunden</p>
              </div>
              <Row xs={1} sm={2} md={3} lg={4} className="g-4">
                {filteredAnimes.map(anime => {
                  const availability = calculateAvailability(anime.id);
                  
                  return (
                    <Col key={anime.id}>
                      <Card className="h-100 anime-card">
                        <div className="card-img-container">
                          <Card.Img 
                            variant="top" 
                            src={anime.cover_image_url ? `/api/cover/${anime.id}` : '/placeholder-cover.jpg'} 
                            alt={`Cover: ${anime.titel_de}`} 
                            className="anime-cover"
                          />
                        </div>
                        <Card.Body>
                          <Card.Title as="h5">
                            <a href={`/anime/${anime.id}`} className="text-decoration-none">
                              {anime.titel_de}
                            </a>
                          </Card.Title>
                          
                          {/* Verfügbarkeitsbadges */}
                          <div className="mb-2">
                            {availability.localCount > 0 && (
                              <Badge bg="success" className="me-1">
                                {availability.localCount} lokal
                              </Badge>
                            )}
                            
                            {availability.onlineCount > 0 && (
                              <Badge bg="info" className="me-1">
                                {availability.onlineCount} online
                              </Badge>
                            )}
                            
                            {availability.totalEpisodes > 0 && (
                              <small className="text-muted">
                                von {availability.totalEpisodes} Episoden
                              </small>
                            )}
                          </div>
                          
                          {/* Fortschrittsbalken */}
                          {availability.totalEpisodes > 0 && (
                            <div className="mb-2">
                              <ProgressBar>
                                <ProgressBar 
                                  variant="success" 
                                  now={(availability.localCount / availability.totalEpisodes) * 100} 
                                  key={1} 
                                />
                                <ProgressBar 
                                  variant="info" 
                                  now={((availability.onlineCount - (availability.localCount && availability.onlineCount ? 1 : 0)) / availability.totalEpisodes) * 100} 
                                  key={2} 
                                />
                              </ProgressBar>
                            </div>
                          )}
                          
                          {/* Links */}
                          {anime.anime_loads_url && (
                            <Button
                              variant="outline-primary"
                              size="sm"
                              className="mt-2"
                              href={anime.anime_loads_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <FaExternalLinkAlt className="me-1" /> Auf Anime-Loads
                            </Button>
                          )}
                        </Card.Body>
                      </Card>
                    </Col>
                  );
                })}
              </Row>
            </>
          )}
        </Tab>
        
        {/* Externer Import-Tab */}
        <Tab eventKey="import" title="Neuen Anime importieren">
          <Card className="mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Anime auf anime-loads.org suchen</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={(e) => { e.preventDefault(); handleExternalSearch(); }}>
                <InputGroup className="mb-3">
                  <Form.Control
                    placeholder="Anime-Titel eingeben..."
                    value={externalSearchQuery}
                    onChange={(e) => setExternalSearchQuery(e.target.value)}
                  />
                  <Button 
                    variant="primary" 
                    onClick={handleExternalSearch}
                    disabled={externalSearchLoading || !externalSearchQuery.trim()}
                  >
                    {externalSearchLoading ? (
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                    ) : (
                      <FaSearch />
                    )}
                  </Button>
                </InputGroup>
              </Form>
              
              {/* Externe Suchergebnisse */}
              {externalSearchError && (
                <Alert variant="danger">
                  {externalSearchError}
                </Alert>
              )}
              
              {externalSearchLoading && (
                <div className="text-center my-3">
                  <Spinner animation="border" variant="primary" />
                  <p>Suche auf anime-loads.org...</p>
                </div>
              )}
              
              {!externalSearchLoading && externalSearchResults.length === 0 && externalSearchQuery && !externalSearchError && (
                <Alert variant="info">
                  Keine Anime-Einträge gefunden für "{externalSearchQuery}".
                </Alert>
              )}
              
              {!externalSearchLoading && externalSearchResults.length > 0 && (
                <div>
                  <h6>Suchergebnisse ({externalSearchResults.length}):</h6>
                  <div className="list-group">
                    {externalSearchResults.map((result, index) => {
                      const alreadyInDb = isAnimeInDatabase(result.title);
                      
                      return (
                        <div key={index} className="list-group-item list-group-item-action">
                          <div className="d-flex w-100 justify-content-between align-items-center">
                            <div>
                              <h6 className="mb-1">{result.title}</h6>
                              {alreadyInDb && (
                                <Badge bg="warning" className="me-2">
                                  <FaExclamationTriangle className="me-1" /> Bereits in Datenbank
                                </Badge>
                              )}
                            </div>
                            <div>
                              <Button
                                variant="outline-primary"
                                size="sm"
                                className="me-2"
                                href={result.url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <FaExternalLinkAlt className="me-1" /> Ansehen
                              </Button>
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => handleScrapeAnime(result.url)}
                              >
                                <FaDownload className="me-1" /> Importieren
                              </Button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
          
          {/* Scraping-Ergebnis */}
          {scrapingLoading && (
            <Card className="mb-4">
              <Card.Header className="bg-light">
                <h5 className="mb-0">Anime wird geladen...</h5>
              </Card.Header>
              <Card.Body className="text-center">
                <Spinner animation="border" variant="primary" />
                <p className="mt-2">Informationen werden von anime-loads.org geladen. Dies kann einen Moment dauern...</p>
              </Card.Body>
            </Card>
          )}
          
          {scrapingError && (
            <Alert variant="danger">
              {scrapingError}
            </Alert>
          )}
          
          {scrapingResult && !scrapingLoading && !scrapingError && (
            <Card className="mb-4">
              <Card.Header className="bg-light d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Anime-Vorschau</h5>
                {importSuccess ? (
                  <Badge bg="success" className="py-2 px-3">
                    <FaCheck className="me-1" /> Import erfolgreich
                  </Badge>
                ) : (
                  <Button
                    variant="success"
                    onClick={handleImportAnime}
                    disabled={importingAnime}
                  >
                    {importingAnime ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-1" /> 
                        Wird importiert...
                      </>
                    ) : (
                      <>
                        <FaDownload className="me-1" /> In meine Bibliothek importieren
                      </>
                    )}
                  </Button>
                )}
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={3}>
                    {scrapingResult.anime.cover_image_url && (
                      <img 
                        src={scrapingResult.anime.cover_image_url} 
                        alt={`Cover: ${scrapingResult.anime.titel_de}`} 
                        className="img-fluid rounded mb-3" 
                      />
                    )}
                  </Col>
                  <Col md={9}>
                    <h4>{scrapingResult.anime.titel_de}</h4>
                    {scrapingResult.anime.titel_jp && (
                      <h6 className="text-muted">{scrapingResult.anime.titel_jp}</h6>
                    )}
                    
                    <div className="mb-3">
                      {scrapingResult.anime.hauptgenre && (
                        <Badge bg="secondary" className="me-1">{scrapingResult.anime.hauptgenre}</Badge>
                      )}
                      {scrapingResult.anime.nebengenres && scrapingResult.anime.nebengenres.split(',').map((genre, idx) => (
                        <Badge key={idx} bg="secondary" className="me-1">{genre.trim()}</Badge>
                      ))}
                    </div>
                    
                    <div className="mb-3">
                      <strong>Typ:</strong> {scrapingResult.anime.typ || 'Unbekannt'}<br />
                      <strong>Jahr:</strong> {scrapingResult.anime.jahr || 'Unbekannt'}<br />
                      <strong>Episoden:</strong> {scrapingResult.anime.episoden_anzahl || 'Unbekannt'}<br />
                      <strong>Laufzeit:</strong> {scrapingResult.anime.laufzeit || 'Unbekannt'}
                    </div>
                    
                    {scrapingResult.anime.beschreibung && (
                      <div className="anime-description">
                        <p>{scrapingResult.anime.beschreibung}</p>
                      </div>
                    )}
                    
                    <h5 className="mt-4">Gefundene Episoden: {scrapingResult.episodes.length}</h5>
                    {scrapingResult.episodes.length > 0 && (
                      <div className="table-responsive">
                        <table className="table table-sm">
                          <thead>
                            <tr>
                              <th>#</th>
                              <th>Titel</th>
                              <th>URL</th>
                            </tr>
                          </thead>
                          <tbody>
                            {scrapingResult.episodes.slice(0, 5).map((episode, idx) => (
                              <tr key={idx}>
                                <td>{episode.episoden_nummer}</td>
                                <td>{episode.titel}</td>
                                <td>
                                  {episode.anime_loads_episode_url && (
                                    <Button
                                      variant="outline-primary"
                                      size="sm"
                                      href={episode.anime_loads_episode_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      <FaExternalLinkAlt />
                                    </Button>
                                  )}
                                </td>
                              </tr>
                            ))}
                            {scrapingResult.episodes.length > 5 && (
                              <tr>
                                <td colSpan={3} className="text-center">
                                  <em>...und {scrapingResult.episodes.length - 5} weitere Episoden</em>
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </Col>
                </Row>
              </Card.Body>
              {importSuccess && (
                <Card.Footer>
                  <Button variant="primary" onClick={() => setActiveTab('browse')}>
                    <FaArrowRight className="me-1" /> Zu meinen Animes gehen
                  </Button>
                </Card.Footer>
              )}
            </Card>
          )}
        </Tab>
        
        {/* Sync-Tab */}
        <Tab eventKey="sync" title="Sync Status">
          <Card className="mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Synchronisationsstatus mit anime-loads.org</h5>
            </Card.Header>
            <Card.Body>
              <p>Hier kannst du den Synchronisationsstatus deiner Anime-Bibliothek mit anime-loads.org überprüfen.</p>
              
              <div className="d-flex justify-content-between mb-3">
                <div>
                  <strong>Animes in Bibliothek:</strong> {animes.length}
                </div>
                <div>
                  <Button variant="outline-primary" size="sm">
                    <FaSync className="me-1" /> Alle aktualisieren
                  </Button>
                </div>
              </div>
              
              <div className="list-group">
                {animes.slice(0, 10).map(anime => {
                  const availability = calculateAvailability(anime.id);
                  const hasOnlineContent = availability.onlineCount > 0;
                  
                  return (
                    <div key={anime.id} className="list-group-item list-group-item-action">
                      <div className="d-flex w-100 justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{anime.titel_de}</h6>
                          <div>
                            {hasOnlineContent ? (
                              <Badge bg="success">Online verfügbar</Badge>
                            ) : (
                              <Badge bg="warning">Nicht online verfügbar</Badge>
                            )}
                            <small className="ms-2 text-muted">
                              {availability.localCount} von {availability.totalEpisodes} Episoden lokal verfügbar
                            </small>
                          </div>
                        </div>
                        <div>
                          {anime.anime_loads_url ? (
                            <Button
                              variant="outline-info"
                              size="sm"
                              className="me-2"
                              href={anime.anime_loads_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <FaExternalLinkAlt className="me-1" /> anime-loads
                            </Button>
                          ) : (
                            <Button
                              variant="outline-warning"
                              size="sm"
                              className="me-2"
                              disabled
                            >
                              <FaExclamationTriangle className="me-1" /> Keine URL
                            </Button>
                          )}
                          <Button
                            variant="outline-primary"
                            size="sm"
                            href={`/anime/${anime.id}`}
                          >
                            Details
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {animes.length > 10 && (
                  <div className="list-group-item text-center">
                    <Button variant="link">Mehr anzeigen</Button>
                  </div>
                )}
              </div>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default AvailableAnimes;
