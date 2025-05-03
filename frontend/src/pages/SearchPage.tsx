import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Container, Row, Col, Spinner, Alert, Button } from 'react-bootstrap';
import { animeService } from '../services/api';
import { Anime } from '../types';
import AnimeCard from '../components/AnimeCard';

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const suchBegriff = searchParams.get('q') || '';
  
  const [animes, setAnimes] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Nur suchen, wenn ein Suchbegriff vorhanden ist
    if (!suchBegriff) {
      setAnimes([]);
      return;
    }

    const sucheDurchführen = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await animeService.searchAnimes(suchBegriff);
        
        if (response.error) {
          setError(response.error);
        } else if (response.data) {
          setAnimes(response.data.items || []);
        }
      } catch (err) {
        setError('Ein Fehler ist bei der Suche aufgetreten.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    sucheDurchführen();
  }, [suchBegriff]);

  return (
    <Container>
      <h1 className="mb-4">Suchergebnisse für: {suchBegriff}</h1>

      {/* Lade-Indikator */}
      {loading && (
        <div className="text-center my-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Suche läuft...</p>
        </div>
      )}

      {/* Fehlermeldung */}
      {error && (
        <Alert variant="danger">
          Fehler bei der Suche: {error}
        </Alert>
      )}

      {/* Keine Ergebnisse */}
      {!loading && !error && animes.length === 0 && (
        <Alert variant="info">
          Keine Animes für "{suchBegriff}" gefunden.
        </Alert>
      )}

      {/* Anime-Karten-Grid */}
      {!loading && !error && animes.length > 0 && (
        <>
          <p>Gefunden: {animes.length} Anime(s)</p>
          <Row xs={1} sm={2} md={3} lg={4} className="g-4">
            {animes.map(anime => (
              <Col key={anime.id}>
                <AnimeCard anime={anime} />
              </Col>
            ))}
          </Row>
        </>
      )}

      {/* Zurück-Button */}
      <div className="mt-4">
        <Button variant="secondary" onClick={() => window.history.back()}>
          Zurück
        </Button>
      </div>
    </Container>
  );
};

export default SearchPage;
