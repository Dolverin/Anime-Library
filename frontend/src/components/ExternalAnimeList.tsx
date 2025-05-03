import React from 'react';
import { Card, Button, Row, Col, Image, Spinner } from 'react-bootstrap';
import { ExternalAnimeSearchResult } from '../types';

interface ExternalAnimeListProps {
  animes: ExternalAnimeSearchResult[];
  isLoading: boolean;
  onImportClick: (animeUrl: string) => void;
  isImporting: Record<string, boolean>; // Speichert den Lade-Status pro Anime-ID
}

const ExternalAnimeList: React.FC<ExternalAnimeListProps> = ({ 
  animes, 
  isLoading, 
  onImportClick,
  isImporting 
}) => {
  if (isLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Lade Animes...</span>
        </Spinner>
        <p className="mt-2">Suche auf anime-loads.org...</p>
      </div>
    );
  }

  if (animes.length === 0) {
    return <p className="text-center my-3">Keine Ergebnisse gefunden.</p>;
  }

  return (
    <Row xs={1} md={2} lg={3} className="g-4 mt-2">
      {animes.map((anime) => (
        <Col key={anime.id}>
          <Card className="h-100 shadow-sm">
            {anime.image_url ? (
              <div className="text-center pt-3" style={{ height: '200px' }}>
                <Image 
                  src={anime.image_url} 
                  alt={anime.title} 
                  style={{ maxHeight: '180px', maxWidth: '100%', objectFit: 'contain' }}
                />
              </div>
            ) : (
              <div 
                className="text-center d-flex align-items-center justify-content-center" 
                style={{ height: '200px', backgroundColor: '#f8f9fa' }}
              >
                <span className="text-muted">Kein Bild verfügbar</span>
              </div>
            )}
            <Card.Body className="d-flex flex-column">
              <Card.Title>{anime.title}</Card.Title>
              <div className="mt-auto pt-3">
                <Button 
                  variant="primary" 
                  onClick={() => onImportClick(anime.url)} 
                  disabled={isImporting[anime.id]}
                  className="w-100"
                >
                  {isImporting[anime.id] ? (
                    <>
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="me-2"
                      />
                      Importiere...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-cloud-download me-2"></i>
                      Anime importieren
                    </>
                  )}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default ExternalAnimeList;
