import React, { useState } from 'react';
import { Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { animeService } from '../services/api';

interface ImportLocalFilesModalProps {
  show: boolean;
  onHide: () => void;
  onSuccess: () => void;
}

const ImportLocalFilesModal: React.FC<ImportLocalFilesModalProps> = ({ show, onHide, onSuccess }) => {
  const [importPath, setImportPath] = useState<string>('/mnt/mediathek/Anime');
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<{
    total_files: number;
    matched_animes: number;
    updated_episodes: number;
  } | null>(null);
  const [createNew, setCreateNew] = useState<boolean>(true);

  const handleImport = async () => {
    if (!importPath.trim()) {
      setImportError('Bitte gib einen gültigen Pfad ein.');
      return;
    }

    setIsImporting(true);
    setImportError(null);
    setImportResult(null);

    try {
      // Je nach Einstellung entweder normale Scan-Funktion oder Scan-and-Create verwenden
      const response = createNew 
        ? await animeService.scanAndCreateAnimes(importPath)
        : await animeService.scanLocalFiles(importPath);
      
      if (response.error) {
        const errorMessage = typeof response.error === 'string' 
          ? response.error 
          : JSON.stringify(response.error);
        console.error('Import error details:', errorMessage);
        setImportError(errorMessage);
      } else if (response.data) {
        setImportResult(response.data);
        
        // Erfolgreiche Importbenachrichtigung
        setTimeout(() => {
          onSuccess();
          onHide();
        }, 3000);
      }
    } catch (err) {
      console.error('Import error:', err);
      const errorMessage = err instanceof Error 
        ? `${err.name}: ${err.message}` 
        : 'Ein unerwarteter Fehler ist aufgetreten.';
      setImportError(errorMessage);
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Lokale Anime-Dateien importieren</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group>
            <Form.Label>Verzeichnispfad</Form.Label>
            <Form.Control
              type="text"
              value={importPath}
              onChange={(e) => setImportPath(e.target.value)}
              placeholder="/pfad/zu/anime/dateien"
              disabled={isImporting}
            />
            <Form.Text className="text-muted">
              Gib den Pfad zum Verzeichnis mit deinen Anime-Dateien ein.
            </Form.Text>
          </Form.Group>
          
          <Form.Group className="mt-3">
            <Form.Check
              type="checkbox"
              label="Animes automatisch erstellen, wenn nicht in der Datenbank vorhanden"
              checked={createNew}
              onChange={(e) => setCreateNew(e.target.checked)}
              disabled={isImporting}
            />
            <Form.Text className="text-muted">
              Wenn aktiviert, werden neue Animes basierend auf den Dateinamen erstellt.
            </Form.Text>
          </Form.Group>
        </Form>

        {importError && (
          <Alert variant="danger" className="mt-3">
            {importError}
          </Alert>
        )}

        {importResult && (
          <Alert variant="success" className="mt-3">
            <p className="mb-0">Import erfolgreich!</p>
            <ul className="mb-0 mt-2">
              <li>Gefundene Dateien: {importResult.total_files}</li>
              <li>Zugeordnete/Erstellte Animes: {importResult.matched_animes}</li>
              <li>Aktualisierte Episoden: {importResult.updated_episodes}</li>
            </ul>
          </Alert>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={isImporting}>
          Schließen
        </Button>
        <Button 
          variant="primary" 
          onClick={handleImport} 
          disabled={isImporting || !importPath.trim()}
        >
          {isImporting ? (
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
            'Importieren starten'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ImportLocalFilesModal;
