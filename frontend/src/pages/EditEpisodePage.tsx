import { useState, useEffect } from 'react';
import { Container, Alert, Button, Spinner } from 'react-bootstrap';
import { useNavigate, useParams } from 'react-router-dom';
import EpisodeForm from '../components/EpisodeForm';
import { EpisodeCreate } from '../types';
import { episodeService } from '../services/api';

const EditEpisodePage = () => {
  const { animeId, episodeId } = useParams<{ animeId: string; episodeId: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [initialData, setInitialData] = useState<Partial<EpisodeCreate>>({});

  useEffect(() => {
    const fetchEpisodeDetails = async () => {
      if (!animeId || !episodeId) return;
      
      setIsLoading(true);
      try {
        const response = await episodeService.getEpisode(parseInt(animeId), parseInt(episodeId));
        
        if (response.error) {
          setError(response.error);
        } else if (response.data) {
          // Daten für das Formular vorbereiten
          const formData: Partial<EpisodeCreate> = {
            episoden_nummer: response.data.episoden_nummer,
            titel: response.data.titel,
            status: response.data.status,
            air_date: response.data.air_date ? new Date(response.data.air_date).toISOString().split('T')[0] : undefined,
            anime_loads_episode_url: response.data.anime_loads_episode_url || undefined
          };
          
          setInitialData(formData);
        }
      } catch (err) {
        console.error('Fehler beim Laden der Episode-Details:', err);
        setError('Ein Fehler ist beim Abrufen der Episode-Details aufgetreten.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEpisodeDetails();
  }, [animeId, episodeId]);

  const handleSubmit = async (data: EpisodeCreate) => {
    if (!episodeId) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Nur die aktualisierten Felder senden
      const updateData: Partial<EpisodeCreate> = {};
      
      // Felder nur hinzufügen, wenn sie im Formular ausgefüllt wurden
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '' && key !== 'anime_id') {
          (updateData as any)[key] = value;
        }
      });
      
      const response = await episodeService.updateEpisode(parseInt(episodeId), updateData);
      
      if (response.error) {
        setError(response.error);
      } else {
        setSuccess(true);
        
        // Kurz warten und dann zur Detailseite zurücknavigieren
        setTimeout(() => {
          navigate(`/anime/${animeId}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Fehler beim Aktualisieren der Episode:', err);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!animeId || !episodeId) {
    return (
      <Container className="py-4">
        <Alert variant="danger">
          Unvollständige Parameter. Bitte gehe zurück zur Anime-Übersicht.
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

  if (isLoading) {
    return (
      <Container className="text-center my-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2">Lade Episode-Details...</p>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Episode bearbeiten</h1>
        <Button 
          variant="outline-secondary" 
          onClick={() => navigate(`/anime/${animeId}`)}
        >
          Zurück zum Anime
        </Button>
      </div>

      {success && (
        <Alert variant="success" className="mb-4">
          Episode wurde erfolgreich aktualisiert! Du wirst zur Anime-Detailseite weitergeleitet...
        </Alert>
      )}

      <EpisodeForm 
        animeId={parseInt(animeId)}
        initialData={initialData}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        error={error}
        isEditing={true}
      />
    </Container>
  );
};

export default EditEpisodePage;
