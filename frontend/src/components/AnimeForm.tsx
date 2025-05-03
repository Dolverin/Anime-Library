import { useState, useEffect } from 'react';
import { Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { AnimeCreate, AnimeStatus } from '../types';

interface AnimeFormProps {
  initialData?: Partial<AnimeCreate>;
  onSubmit: (data: AnimeCreate) => Promise<void>;
  isEditing?: boolean;
  isSubmitting?: boolean;
  error?: string | null;
}

const AnimeForm: React.FC<AnimeFormProps> = ({
  initialData = {},
  onSubmit,
  isEditing = false,
  isSubmitting = false,
  error = null
}) => {
  const [formData, setFormData] = useState<AnimeCreate>({
    titel_de: '',
    status: AnimeStatus.PLAN_TO_WATCH,
    ...initialData
  });

  const [validation, setValidation] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (initialData) {
      setFormData(prevData => ({ ...prevData, ...initialData }));
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: name === 'jahr' ? (value ? parseInt(value) : undefined) : value
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
    
    if (!formData.titel_de.trim()) {
      errors.titel_de = 'Der deutsche Titel ist erforderlich.';
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
          <Form.Label>Deutscher Titel *</Form.Label>
          <Form.Control
            type="text"
            name="titel_de"
            value={formData.titel_de}
            onChange={handleChange}
            isInvalid={!!validation.titel_de}
            required
          />
          <Form.Control.Feedback type="invalid">
            {validation.titel_de}
          </Form.Control.Feedback>
          <Form.Text className="text-muted">
            Pflichtfeld
          </Form.Text>
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Englischer Titel</Form.Label>
          <Form.Control
            type="text"
            name="titel_en"
            value={formData.titel_en || ''}
            onChange={handleChange}
          />
        </Form.Group>
      </Row>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Japanischer Titel (Romanisiert)</Form.Label>
          <Form.Control
            type="text"
            name="titel_jp"
            value={formData.titel_jp || ''}
            onChange={handleChange}
          />
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Originaltitel</Form.Label>
          <Form.Control
            type="text"
            name="titel_org"
            value={formData.titel_org || ''}
            onChange={handleChange}
          />
        </Form.Group>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label>Alternative Titel/Synonyme</Form.Label>
        <Form.Control
          type="text"
          name="synonyme"
          value={formData.synonyme || ''}
          onChange={handleChange}
          placeholder="Verschiedene Titel durch Kommas trennen"
        />
      </Form.Group>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Status</Form.Label>
          <Form.Select
            name="status"
            value={formData.status || AnimeStatus.PLAN_TO_WATCH}
            onChange={handleChange}
          >
            <option value={AnimeStatus.PLAN_TO_WATCH}>Geplant</option>
            <option value={AnimeStatus.WATCHING}>Schaue ich</option>
            <option value={AnimeStatus.COMPLETED}>Abgeschlossen</option>
            <option value={AnimeStatus.ON_HOLD}>Pausiert</option>
            <option value={AnimeStatus.DROPPED}>Abgebrochen</option>
          </Form.Select>
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Typ</Form.Label>
          <Form.Control
            type="text"
            name="typ"
            value={formData.typ || ''}
            onChange={handleChange}
            placeholder="z.B. TV, Movie, OVA"
          />
        </Form.Group>
      </Row>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Jahr</Form.Label>
          <Form.Control
            type="number"
            name="jahr"
            value={formData.jahr || ''}
            onChange={handleChange}
            min={1950}
            max={new Date().getFullYear() + 2}
          />
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Episoden</Form.Label>
          <Form.Control
            type="text"
            name="episoden_anzahl"
            value={formData.episoden_anzahl || ''}
            onChange={handleChange}
            placeholder="z.B. 12, 24+2 OVA"
          />
        </Form.Group>
      </Row>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Hauptgenre</Form.Label>
          <Form.Control
            type="text"
            name="hauptgenre"
            value={formData.hauptgenre || ''}
            onChange={handleChange}
          />
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>Nebengenres</Form.Label>
          <Form.Control
            type="text"
            name="nebengenres"
            value={formData.nebengenres || ''}
            onChange={handleChange}
            placeholder="Genres durch Kommas trennen"
          />
        </Form.Group>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label>Tags</Form.Label>
        <Form.Control
          type="text"
          name="tags"
          value={formData.tags || ''}
          onChange={handleChange}
          placeholder="Tags durch Kommas trennen"
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Laufzeit</Form.Label>
        <Form.Control
          type="text"
          name="laufzeit"
          value={formData.laufzeit || ''}
          onChange={handleChange}
          placeholder="z.B. 24 Min. pro Episode"
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Beschreibung</Form.Label>
        <Form.Control
          as="textarea"
          rows={4}
          name="beschreibung"
          value={formData.beschreibung || ''}
          onChange={handleChange}
        />
      </Form.Group>

      <Row className="mb-3">
        <Form.Group as={Col} md={6}>
          <Form.Label>Anime-Loads URL</Form.Label>
          <Form.Control
            type="url"
            name="anime_loads_url"
            value={formData.anime_loads_url || ''}
            onChange={handleChange}
            placeholder="https://anime-loads.org/anime/..."
          />
        </Form.Group>

        <Form.Group as={Col} md={6}>
          <Form.Label>AniSearch URL</Form.Label>
          <Form.Control
            type="url"
            name="anisearch_url"
            value={formData.anisearch_url || ''}
            onChange={handleChange}
            placeholder="https://anisearch.de/anime/..."
          />
        </Form.Group>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label>Cover-Bild URL</Form.Label>
        <Form.Control
          type="url"
          name="cover_image_url"
          value={formData.cover_image_url || ''}
          onChange={handleChange}
          placeholder="URL zu einem Bild"
        />
        <Form.Text className="text-muted">
          Direktlink zu einem Bild. Das Bild wird automatisch heruntergeladen und gespeichert.
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

export default AnimeForm;
