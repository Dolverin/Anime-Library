import { useState, useEffect } from 'react';
import { Container, Alert, Button, Spinner } from 'react-bootstrap';
import { useNavigate, useParams } from 'react-router-dom';
import AnimeForm from '../components/AnimeForm';
import { AnimeUpdate, AnimeCreate } from '../types';
import { animeService } from '../services/api';

const EditAnimePage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [initialData, setInitialData] = useState<Partial<AnimeCreate>>({});

  useEffect(() => {
    const fetchAnimeDetails = async () => {
      if (!id) return;
      
      setIsLoading(true);
      try {
        const response = await animeService.getAnime(parseInt(id));
        
        if (response.error) {
          setError(response.error);
        } else if (response.data) {
          // Daten für das Formular vorbereiten - Typkonvertierung um das AnimeCreate-Format zu erfüllen
          const formData: Partial<AnimeCreate> = {
            titel_de: response.data.titel_de,
            titel_jp: response.data.titel_jp || undefined,
            titel_org: response.data.titel_org || undefined, 
            titel_en: response.data.titel_en || undefined,
            synonyme: response.data.synonyme || undefined,
            status: response.data.status,
            beschreibung: response.data.beschreibung || undefined,
            anime_loads_url: response.data.anime_loads_url || undefined,
            cover_image_url: response.data.cover_image_url || undefined,
            typ: response.data.typ || undefined,
            jahr: response.data.jahr || undefined,
            episoden_anzahl: response.data.episoden_anzahl || undefined,
            laufzeit: response.data.laufzeit || undefined,
            hauptgenre: response.data.hauptgenre || undefined,
            nebengenres: response.data.nebengenres || undefined,
            tags: response.data.tags || undefined,
            anisearch_url: response.data.anisearch_url || undefined
          };
          
          setInitialData(formData);
        }
      } catch (err) {
        console.error('Fehler beim Laden der Anime-Details:', err);
        setError('Ein Fehler ist beim Abrufen der Anime-Details aufgetreten.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnimeDetails();
  }, [id]);

  const handleSubmit = async (data: AnimeCreate) => {
    if (!id) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Nur die aktualisierten Felder senden
      const updateData: AnimeUpdate = {};
      
      // Felder nur hinzufügen, wenn sie im Formular ausgefüllt wurden
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          (updateData as any)[key] = value;
        }
      });
      
      const response = await animeService.updateAnime(parseInt(id), updateData);
      
      if (response.error) {
        setError(response.error);
      } else {
        setSuccess(true);
        
        // Kurz warten und dann zur Detailseite zurücknavigieren
        setTimeout(() => {
          navigate(`/anime/${id}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Fehler beim Aktualisieren des Animes:', err);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <Container className="text-center my-5">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2">Lade Anime-Details...</p>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Anime bearbeiten</h1>
        <Button 
          variant="outline-secondary" 
          onClick={() => navigate(`/anime/${id}`)}
        >
          Zurück
        </Button>
      </div>

      {success && (
        <Alert variant="success" className="mb-4">
          Anime wurde erfolgreich aktualisiert! Du wirst zur Detailseite weitergeleitet...
        </Alert>
      )}

      <AnimeForm 
        initialData={initialData}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        error={error}
        isEditing={true}
      />
    </Container>
  );
};

export default EditAnimePage;
