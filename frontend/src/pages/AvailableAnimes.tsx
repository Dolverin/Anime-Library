import { useState, useEffect } from 'react';
import { Container, Row, Col, Spinner, Alert, Form, ToggleButton } from 'react-bootstrap';
import { Anime, Episode, EpisodeAvailabilityStatus } from '../types';
import { animeService, episodeService } from '../services/api';
import AnimeCard from '../components/AnimeCard';

const AvailableAnimes = () => {
  const [animes, setAnimes] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [availabilityFilter, setAvailabilityFilter] = useState<string>('all');
  const [animeWithEpisodes, setAnimeWithEpisodes] = useState<Map<number, Episode[]>>(new Map());

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

  return (
    <Container>
      <h1 className="mb-4">Verfügbare Animes</h1>
      
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

      {/* Anime-Karten-Grid */}
      {!loading && !error && filteredAnimes.length > 0 && (
        <>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <p className="mb-0">{filteredAnimes.length} verfügbare Anime(s) gefunden</p>
          </div>
          <Row xs={1} sm={2} md={3} lg={4} className="g-4">
            {filteredAnimes.map(anime => (
              <Col key={anime.id}>
                <AnimeCard anime={anime} />
              </Col>
            ))}
          </Row>
        </>
      )}
    </Container>
  );
};

export default AvailableAnimes;
