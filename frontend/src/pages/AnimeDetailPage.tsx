import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Spinner, Alert, Form } from 'react-bootstrap';
import { Anime, AnimeStatus, Episode } from '../types';
import { animeService, episodeService } from '../services/api';
import EpisodeList from '../components/EpisodeList';

const AnimeDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [anime, setAnime] = useState<Anime | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<AnimeStatus | string>('');

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

  // Zurück zur Hauptseite
  const goBack = () => {
    navigate(-1);
  };

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
        ← Zurück
      </Button>

      <Card>
        <Card.Header>
          <h2>{anime.titel}</h2>
        </Card.Header>
        <Card.Body>
          <Row>
            {/* Cover-Bild */}
            <Col md={3} className="mb-3">
              <img 
                src={coverUrl} 
                alt={`Cover: ${anime.titel}`} 
                className="img-fluid rounded" 
              />
              
              {/* Status-Dropdown */}
              <Form.Group className="mt-3">
                <Form.Label>Status:</Form.Label>
                <Form.Select 
                  value={selectedStatus}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              {/* Anime-Loads Link */}
              {anime.anime_loads_url && (
                <Button 
                  variant="info" 
                  href={anime.anime_loads_url} 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 w-100"
                >
                  Auf Anime-Loads ansehen
                </Button>
              )}
            </Col>

            {/* Anime-Details */}
            <Col md={9}>
              {/* Beschreibung */}
              <h4>Beschreibung</h4>
              <p>{anime.beschreibung || 'Keine Beschreibung verfügbar.'}</p>
              
              {/* Episodenliste */}
              <h4 className="mt-4">Episoden</h4>
              <EpisodeList 
                animeId={anime.id} 
                episodes={episodes}
              />
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default AnimeDetailPage;
