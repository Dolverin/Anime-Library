import { useState, useEffect } from 'react';
import { Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { EpisodeCreate, EpisodeStatus } from '../types';

interface EpisodeFormProps {
  animeId: number;
  initialData?: Partial<EpisodeCreate>;
  onSubmit: (data: EpisodeCreate) => Promise<void>;
  isEditing?: boolean;
  isSubmitting?: boolean;
  error?: string | null;
}

const EpisodeForm: React.FC<EpisodeFormProps> = ({
  animeId,
  initialData = {},
  onSubmit,
  isEditing = false,
  isSubmitting = false,
  error = null
}) => {
  const [formData, setFormData] = useState<EpisodeCreate>({
    anime_id: animeId,
    episoden_nummer: 1,
    ...initialData
  });

  const [validation, setValidation] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (initialData) {
      setFormData(prevData => ({ ...prevData, ...initialData, anime_id: animeId }));
    }
  }, [initialData, animeId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: name === 'episoden_nummer' ? (value ? parseInt(value) : 1) : value
    }));
    
    // Zurücksetzen der Validierungsmeldung für dieses Feld
    if (validation[name]) {
      setValidation(prev => {
        const newValidation = { ...prev };
        delete newValidation[name];
        return newValidation;
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: { [key: string]: string } = {};
    
    if (!formData.episoden_nummer || formData.episoden_nummer < 1) {
      errors.episoden_nummer = 'Die Episodennummer muss mindestens 1 sein.';
    }
    
    // Weitere Validierungen können hier hinzugefügt werden
    
    setValidation(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    await onSubmit(formData);
  };

  return (
    <Form onSubmit={handleSubmit}>
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Episodennummer *</Form.Label>
          <Form.Control
            type="number"
            name="episoden_nummer"
            value={formData.episoden_nummer}
            onChange={handleChange}
            isInvalid={!!validation.episoden_nummer}
            min={1}
            required
          />
          <Form.Control.Feedback type="invalid">
            {validation.episoden_nummer}
          </Form.Control.Feedback>
          <Form.Text className="text-muted">
            Pflichtfeld
          </Form.Text>
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Titel</Form.Label>
          <Form.Control
            type="text"
            name="titel"
            value={formData.titel || ''}
            onChange={handleChange}
            placeholder="Episodentitel"
          />
        </Form.Group>
      </Row>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Status</Form.Label>
          <Form.Select
            name="status"
            value={formData.status || EpisodeStatus.NICHT_GESEHEN}
            onChange={handleChange}
          >
            <option value={EpisodeStatus.NICHT_GESEHEN}>Nicht gesehen</option>
            <option value={EpisodeStatus.GESEHEN}>Gesehen</option>
          </Form.Select>
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Ausstrahlungsdatum</Form.Label>
          <Form.Control
            type="date"
            name="air_date"
            value={formData.air_date || ''}
            onChange={handleChange}
          />
        </Form.Group>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label>Anime-Loads Episode URL</Form.Label>
        <Form.Control
          type="url"
          name="anime_loads_episode_url"
          value={formData.anime_loads_episode_url || ''}
          onChange={handleChange}
          placeholder="https://anime-loads.org/anime/..."
        />
        <Form.Text className="text-muted">
          Link zur Episode auf Anime-Loads
        </Form.Text>
      </Form.Group>

      <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
        <Button variant="primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              {isEditing ? 'Aktualisiere...' : 'Speichere...'}
            </>
          ) : (
            isEditing ? 'Aktualisieren' : 'Speichern'
          )}
        </Button>
      </div>
    </Form>
  );
};

export default EpisodeForm;
