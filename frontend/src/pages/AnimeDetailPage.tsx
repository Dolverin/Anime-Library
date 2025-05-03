import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Spinner, Alert, Form, Badge, ListGroup, Tab, Tabs } from 'react-bootstrap';
import { Anime, AnimeStatus, Episode, EpisodeStatus } from '../types';
import { animeService, episodeService } from '../services/api';
import EpisodeList from '../components/EpisodeList';
import { FaArrowLeft, FaEdit, FaExternalLinkAlt, FaPlus, FaInfoCircle, FaCalendarAlt, FaFilm, FaLayerGroup, FaClock, FaTag } from 'react-icons/fa';

const AnimeDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [anime, setAnime] = useState<Anime | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<AnimeStatus | string>('');
  const [activeTab, setActiveTab] = useState<string>('episodes');

  useEffect(() => {
    const fetchAnimeDetails = async () => {
      if (!id) return;
      
      setLoading(true);
      
      try {
        // Anime-Details abrufen
        const animeResponse = await animeService.getAnime(parseInt(id));
        
        if (animeResponse.error) {
          setError(animeResponse.error);
        } else if (animeResponse.data) {
          setAnime(animeResponse.data);
          setSelectedStatus(animeResponse.data.status);
          
          // Episoden abrufen
          const episodesResponse = await episodeService.getEpisodesByAnimeId(parseInt(id));
          
          if (episodesResponse.data) {
            setEpisodes(episodesResponse.data);
          }
        }
      } catch (err) {
        setError('Ein Fehler ist beim Abrufen der Daten aufgetreten.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnimeDetails();
  }, [id]);

  // Anime-Status aktualisieren
  const handleStatusChange = async (newStatus: string) => {
    if (!id || !anime) return;
    
    try {
      const response = await animeService.updateAnimeStatus(parseInt(id), newStatus);
      
      if (response.data) {
        setAnime({
          ...anime,
          status: newStatus as AnimeStatus
        });
        setSelectedStatus(newStatus);
      }
    } catch (err) {
      console.error('Fehler beim Aktualisieren des Anime-Status:', err);
    }
  };

  // Status-Labels für die Anzeige
  const statusOptions = [
    { value: AnimeStatus.WATCHING, label: 'Schaue ich' },
    { value: AnimeStatus.COMPLETED, label: 'Abgeschlossen' },
    { value: AnimeStatus.PLAN_TO_WATCH, label: 'Geplant' },
    { value: AnimeStatus.ON_HOLD, label: 'Pausiert' },
    { value: AnimeStatus.DROPPED, label: 'Abgebrochen' }
  ];

  // Status-Farben
  const statusVariants: Record<AnimeStatus, string> = {
    [AnimeStatus.PLAN_TO_WATCH]: 'info',
    [AnimeStatus.WATCHING]: 'primary',
    [AnimeStatus.COMPLETED]: 'success',
    [AnimeStatus.ON_HOLD]: 'warning',
    [AnimeStatus.DROPPED]: 'danger'
  };

  // Zurück zur Hauptseite
  const goBack = () => {
    navigate(-1);
  };

  // Statistiken berechnen
  const calculateStats = () => {
    if (!episodes || episodes.length === 0) {
      return { total: 0, watched: 0, progress: 0 };
    }

    const total = episodes.length;
    const watched = episodes.filter(episode => episode.status === EpisodeStatus.GESEHEN).length;
    const progress = total > 0 ? Math.round((watched / total) * 100) : 0;

    return { total, watched, progress };
  };

  const stats = calculateStats();

  if (loading) {
    return (
      <Container className="text-center my-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2">Lade Anime-Details...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="my-4">
        <Alert variant="danger">
          Fehler: {error}
        </Alert>
        <Button variant="secondary" onClick={goBack}>
          Zurück
        </Button>
      </Container>
    );
  }

  if (!anime) {
    return (
      <Container className="my-4">
        <Alert variant="warning">
          Anime nicht gefunden.
        </Alert>
        <Button variant="secondary" onClick={goBack}>
          Zurück
        </Button>
      </Container>
    );
  }

  // Anime-Cover URL
  const coverUrl = anime.cover_image_url 
    ? `/api/cover/${anime.id}` 
    : '/placeholder-cover.jpg';

  return (
    <Container className="my-4">
      {/* Zurück-Button */}
      <Button variant="outline-secondary" onClick={goBack} className="mb-3">
        <FaArrowLeft className="me-1" /> Zurück
      </Button>

      {/* Anime Header-Bereich mit Cover und Overlay */}
      <div className="anime-detail-container">
        <div className="anime-detail-header">
          <img 
            src={coverUrl} 
            alt={`Cover: ${anime.titel_de}`} 
            className="anime-detail-cover" 
          />
          <div className="anime-detail-overlay">
            <div className="anime-detail-title">
              {anime.titel_de}
              {anime.titel_jp && <small className="d-block">{anime.titel_jp}</small>}
            </div>
            
            <div className="anime-detail-info">
              <Badge bg={statusVariants[anime.status as AnimeStatus] || 'secondary'} className="py-2 px-3">
                {statusOptions.find(opt => opt.value === anime.status)?.label || anime.status}
              </Badge>
              
              {anime.jahr && (
                <Badge bg="secondary" className="py-2 px-3">
                  <FaCalendarAlt className="me-1" /> {anime.jahr}
                </Badge>
              )}
              
              {anime.typ && (
                <Badge bg="secondary" className="py-2 px-3">
                  <FaFilm className="me-1" /> {anime.typ}
                </Badge>
              )}
              
              {anime.episoden_anzahl && (
                <Badge bg="secondary" className="py-2 px-3">
                  <FaLayerGroup className="me-1" /> {anime.episoden_anzahl} Folgen
                </Badge>
              )}
              
              {anime.laufzeit && (
                <Badge bg="secondary" className="py-2 px-3">
                  <FaClock className="me-1" /> {anime.laufzeit}
                </Badge>
              )}
            </div>
            
            <div className="d-flex gap-2 mt-2">
              <Button 
                variant="primary"
                size="sm"
                onClick={() => navigate(`/anime/${anime.id}/bearbeiten`)}
              >
                <FaEdit className="me-1" /> Bearbeiten
              </Button>
              
              {anime.anime_loads_url && (
                <Button 
                  variant="secondary" 
                  size="sm"
                  href={anime.anime_loads_url} 
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FaExternalLinkAlt className="me-1" /> Anime-Loads
                </Button>
              )}
            </div>
          </div>
        </div>
        
        {/* Anime-Details und Episoden */}
        <div className="anime-detail-content">
          <Row>
            <Col lg={3} md={4}>
              <Card className="mb-4">
                <Card.Header className="bg-light">
                  <h5 className="mb-0">Status</h5>
                </Card.Header>
                <Card.Body>
                  <Form.Group>
                    <Form.Select 
                      value={selectedStatus}
                      onChange={(e) => handleStatusChange(e.target.value)}
                      className="mb-3"
                    >
                      {statusOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                  
                  <div className="progress mb-2">
                    <div 
                      className="progress-bar" 
                      role="progressbar" 
                      style={{ width: `${stats.progress}%` }} 
                      aria-valuenow={stats.progress} 
                      aria-valuemin={0} 
                      aria-valuemax={100}
                    >
                      {stats.progress}%
                    </div>
                  </div>
                  <small className="text-muted">{stats.watched} von {stats.total} Episoden gesehen</small>
                </Card.Body>
              </Card>
              
              <Card className="mb-4">
                <Card.Header className="bg-light">
                  <h5 className="mb-0">Information</h5>
                </Card.Header>
                <ListGroup variant="flush">
                  {anime.hauptgenre && (
                    <ListGroup.Item>
                      <strong>Hauptgenre:</strong> {anime.hauptgenre}
                    </ListGroup.Item>
                  )}
                  
                  {anime.nebengenres && (
                    <ListGroup.Item>
                      <strong>Nebengenres:</strong> {anime.nebengenres}
                    </ListGroup.Item>
                  )}
                  
                  {anime.tags && (
                    <ListGroup.Item>
                      <strong>Tags:</strong> 
                      <div className="mt-1">
                        {anime.tags.split(',').map((tag, index) => (
                          <Badge 
                            key={index} 
                            bg="light" 
                            text="dark" 
                            className="me-1 mb-1"
                          >
                            <FaTag className="me-1" />{tag.trim()}
                          </Badge>
                        ))}
                      </div>
                    </ListGroup.Item>
                  )}
                  
                  {anime.anisearch_url && (
                    <ListGroup.Item>
                      <a 
                        href={anime.anisearch_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-decoration-none"
                      >
                        <FaExternalLinkAlt className="me-1" /> Auf AniSearch ansehen
                      </a>
                    </ListGroup.Item>
                  )}
                  
                  <ListGroup.Item>
                    <small className="text-muted">
                      Hinzugefügt: {new Date(anime.hinzugefuegt_am).toLocaleDateString()}
                      <br />
                      Aktualisiert: {new Date(anime.zuletzt_aktualisiert_am).toLocaleDateString()}
                    </small>
                  </ListGroup.Item>
                </ListGroup>
              </Card>
            </Col>
            
            <Col lg={9} md={8}>
              <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k || 'episodes')}
                className="mb-4"
              >
                <Tab eventKey="description" title={<><FaInfoCircle className="me-1" /> Beschreibung</>}>
                  <div className="anime-description">
                    {anime.beschreibung ? (
                      <p className="mb-0">{anime.beschreibung}</p>
                    ) : (
                      <p className="mb-0 text-muted">Keine Beschreibung verfügbar.</p>
                    )}
                  </div>
                </Tab>
                
                <Tab eventKey="episodes" title={<><FaLayerGroup className="me-1" /> Episoden ({episodes.length})</>}>
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4>Episoden</h4>
                    <Button 
                      variant="outline-success"
                      size="sm"
                      onClick={() => navigate(`/anime/${anime.id}/episode/hinzufuegen`)}
                    >
                      <FaPlus className="me-1" /> Neue Episode
                    </Button>
                  </div>
                  
                  {episodes.length === 0 ? (
                    <Alert variant="info">
                      Keine Episoden gefunden. Füge neue Episoden hinzu.
                    </Alert>
                  ) : (
                    <EpisodeList 
                      animeId={anime.id} 
                      episodes={episodes}
                      onDeleteEpisode={async (episodeId) => {
                        try {
                          await episodeService.deleteEpisode(episodeId);
                          // Episode aus dem lokalen State entfernen
                          setEpisodes(episodes.filter(ep => ep.id !== episodeId));
                        } catch (err) {
                          console.error('Fehler beim Löschen der Episode:', err);
                          alert('Fehler beim Löschen der Episode.');
                        }
                      }}
                    />
                  )}
                </Tab>
              </Tabs>
            </Col>
          </Row>
        </div>
      </div>
    </Container>
  );
};

export default AnimeDetailPage;
