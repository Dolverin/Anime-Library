import { useState, useEffect } from 'react';
import { Container, Row, Col, Spinner, Alert, Form } from 'react-bootstrap';
import { AnimeStatus, Anime } from '../types';
import { animeService } from '../services/api';
import AnimeCard from '../components/AnimeCard';

const HomePage = () => {
  const [animes, setAnimes] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    const fetchAnimes = async () => {
      setLoading(true);
      const response = await animeService.getAllAnimes();
      
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setAnimes(response.data.items || []);
      }
      
      setLoading(false);
    };

    fetchAnimes();
  }, []);

  // Filtere Animes basierend auf dem ausgewählten Status
  const filteredAnimes = statusFilter === 'all'
    ? animes
    : animes.filter(anime => anime.status === statusFilter);

  return (
    <Container>
      <h1 className="mb-4">Meine Anime-Bibliothek</h1>
      
      {/* Status-Filter */}
      <Form.Group className="mb-4">
        <Form.Label>Nach Status filtern:</Form.Label>
        <Form.Select 
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">Alle anzeigen</option>
          <option value={AnimeStatus.WATCHING}>Schaue ich</option>
          <option value={AnimeStatus.COMPLETED}>Abgeschlossen</option>
          <option value={AnimeStatus.PLAN_TO_WATCH}>Geplant</option>
          <option value={AnimeStatus.ON_HOLD}>Pausiert</option>
          <option value={AnimeStatus.DROPPED}>Abgebrochen</option>
        </Form.Select>
      </Form.Group>

      {/* Lade-Indikator */}
      {loading && (
        <div className="text-center my-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Lade Animes...</p>
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
          Keine Animes gefunden. Füge neue Animes hinzu oder ändere den Filter.
        </Alert>
      )}

      {/* Anime-Karten-Grid */}
      {!loading && !error && filteredAnimes.length > 0 && (
        <Row xs={1} sm={2} md={3} lg={4} className="g-4">
          {filteredAnimes.map(anime => (
            <Col key={anime.id}>
              <AnimeCard anime={anime} />
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default HomePage;
