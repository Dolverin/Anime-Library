import { useState } from 'react';
import { Container, Alert, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import AnimeForm from '../components/AnimeForm';
import { AnimeCreate } from '../types';
import { animeService } from '../services/api';

const AddAnimePage = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (data: AnimeCreate) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await animeService.createAnime(data);
      
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setSuccess(true);
        
        // Kurz warten und dann zur Detailseite des neuen Animes navigieren
        setTimeout(() => {
          if (response.data?.id) {
            navigate(`/anime/${response.data.id}`);
          } else {
            navigate('/meine-animes');
          }
        }, 1500);
      }
    } catch (err) {
      console.error('Fehler beim Erstellen des Animes:', err);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Neuen Anime hinzufügen</h1>
        <Button 
          variant="outline-secondary" 
          onClick={() => navigate(-1)}
        >
          Zurück
        </Button>
      </div>

      {success && (
        <Alert variant="success" className="mb-4">
          Anime wurde erfolgreich erstellt! Du wirst zur Detailseite weitergeleitet...
        </Alert>
      )}

      <p className="text-muted mb-4">
        Fülle das Formular aus, um einen neuen Anime zu deiner Bibliothek hinzuzufügen. 
        Nur der deutsche Titel ist erforderlich, alle anderen Felder sind optional.
      </p>

      <AnimeForm 
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        error={error}
      />
    </Container>
  );
};

export default AddAnimePage;
