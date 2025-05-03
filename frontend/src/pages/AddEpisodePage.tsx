import { useState } from 'react';
import { Container, Alert, Button } from 'react-bootstrap';
import { useNavigate, useParams } from 'react-router-dom';
import EpisodeForm from '../components/EpisodeForm';
import { EpisodeCreate } from '../types';
import { episodeService } from '../services/api';

const AddEpisodePage = () => {
  const { animeId } = useParams<{ animeId: string }>();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (data: EpisodeCreate) => {
    if (!animeId) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const response = await episodeService.createEpisode(parseInt(animeId), data);
      
      if (response.error) {
        setError(response.error);
      } else {
        setSuccess(true);
        
        // Kurz warten und dann zur Detailseite des Animes zurücknavigieren
        setTimeout(() => {
          navigate(`/anime/${animeId}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Fehler beim Erstellen der Episode:', err);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!animeId) {
    return (
      <Container className="py-4">
        <Alert variant="danger">
          Keine Anime-ID gefunden. Bitte gehe zurück zur Anime-Übersicht.
        </Alert>
        <Button 
          variant="secondary" 
          onClick={() => navigate('/meine-animes')}
        >
          Zurück zur Übersicht
        </Button>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Neue Episode hinzufügen</h1>
        <Button 
          variant="outline-secondary" 
          onClick={() => navigate(`/anime/${animeId}`)}
        >
          Zurück zum Anime
        </Button>
      </div>

      {success && (
        <Alert variant="success" className="mb-4">
          Episode wurde erfolgreich erstellt! Du wirst zur Anime-Detailseite weitergeleitet...
        </Alert>
      )}

      <p className="text-muted mb-4">
        Fülle das Formular aus, um eine neue Episode hinzuzufügen. 
        Nur die Episodennummer ist erforderlich, alle anderen Felder sind optional.
      </p>

      <EpisodeForm 
        animeId={parseInt(animeId)}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        error={error}
      />
    </Container>
  );
};

export default AddEpisodePage;
