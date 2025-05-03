import { Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Anime, AnimeStatus } from '../types';

// Übersetzung der Status-Werte für die Anzeige
const statusLabels: Record<AnimeStatus, string> = {
  [AnimeStatus.PLAN_TO_WATCH]: 'Geplant',
  [AnimeStatus.WATCHING]: 'Schaue ich',
  [AnimeStatus.COMPLETED]: 'Abgeschlossen',
  [AnimeStatus.ON_HOLD]: 'Pausiert',
  [AnimeStatus.DROPPED]: 'Abgebrochen'
};

// Farben für die verschiedenen Status
const statusVariants: Record<AnimeStatus, string> = {
  [AnimeStatus.PLAN_TO_WATCH]: 'info',
  [AnimeStatus.WATCHING]: 'primary',
  [AnimeStatus.COMPLETED]: 'success',
  [AnimeStatus.ON_HOLD]: 'warning',
  [AnimeStatus.DROPPED]: 'danger'
};

interface AnimeCardProps {
  anime: Anime;
}

const AnimeCard: React.FC<AnimeCardProps> = ({ anime }) => {
  // Fallback-Bild, falls kein Cover vorhanden
  const coverUrl = anime.cover_image_url 
    ? `/api/cover/${anime.id}` 
    : '/placeholder-cover.jpg';

  // Kürze die Beschreibung, wenn sie zu lang ist
  const kurzeBeschreibung = anime.beschreibung && anime.beschreibung.length > 100
    ? `${anime.beschreibung.substring(0, 100)}...`
    : anime.beschreibung;

  return (
    <Card className="h-100 anime-card">
      <div className="card-img-container">
        <Card.Img 
          variant="top" 
          src={coverUrl} 
          alt={`Cover: ${anime.titel}`} 
          className="anime-cover"
        />
      </div>
      <Card.Body>
        <Card.Title as="h5">
          <Link to={`/anime/${anime.id}`} className="text-decoration-none">
            {anime.titel}
          </Link>
        </Card.Title>
        <Badge 
          bg={statusVariants[anime.status as AnimeStatus] || 'secondary'}
          className="mb-2"
        >
          {statusLabels[anime.status as AnimeStatus] || anime.status}
        </Badge>
        {kurzeBeschreibung && (
          <Card.Text className="small text-muted mt-2">
            {kurzeBeschreibung}
          </Card.Text>
        )}
      </Card.Body>
      <Card.Footer className="text-end bg-transparent">
        <small className="text-muted">
          {anime.episodes?.length || 0} Episoden
        </small>
      </Card.Footer>
    </Card>
  );
};

export default AnimeCard;
