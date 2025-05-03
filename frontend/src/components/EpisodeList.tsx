import { Table, Form, Badge, Button } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import { Episode, EpisodeStatus, EpisodeAvailabilityStatus } from '../types';
import { episodeService } from '../services/api';

// Übersetzung der Status-Werte für die Anzeige
const availabilityLabels: Record<EpisodeAvailabilityStatus, string> = {
  [EpisodeAvailabilityStatus.NOT_AVAILABLE]: 'Nicht verfügbar',
  [EpisodeAvailabilityStatus.AVAILABLE_ONLINE]: 'Online verfügbar',
  [EpisodeAvailabilityStatus.OWNED]: 'Lokal verfügbar',
  [EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE]: 'Lokal & Online'
};

// Farben für die verschiedenen Status
const availabilityVariants: Record<EpisodeAvailabilityStatus, string> = {
  [EpisodeAvailabilityStatus.NOT_AVAILABLE]: 'danger',
  [EpisodeAvailabilityStatus.AVAILABLE_ONLINE]: 'info',
  [EpisodeAvailabilityStatus.OWNED]: 'success',
  [EpisodeAvailabilityStatus.OWNED_AND_AVAILABLE_ONLINE]: 'success'
};

interface EpisodeListProps {
  animeId: number;
  episodes?: Episode[];
  onEpisodeStatusChange?: (episodeId: number, newStatus: EpisodeStatus) => void;
}

const EpisodeList: React.FC<EpisodeListProps> = ({ 
  animeId, 
  episodes: propEpisodes,
  onEpisodeStatusChange 
}) => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Lade Episoden, wenn keine übergeben wurden
  useEffect(() => {
    if (propEpisodes) {
      setEpisodes(propEpisodes);
      return;
    }

    const fetchEpisodes = async () => {
      setLoading(true);
      const response = await episodeService.getEpisodesByAnimeId(animeId);
      
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setEpisodes(response.data);
      }
      
      setLoading(false);
    };

    fetchEpisodes();
  }, [animeId, propEpisodes]);

  // Status einer Episode ändern
  const handleStatusChange = async (episodeId: number, newStatus: EpisodeStatus) => {
    try {
      await episodeService.updateEpisodeStatus(episodeId, newStatus);
      
      // Lokalen State aktualisieren
      setEpisodes(episodes.map(episode => {
        if (episode.id === episodeId) {
          return { ...episode, status: newStatus };
        }
        return episode;
      }));
      
      // Callback aufrufen falls vorhanden
      if (onEpisodeStatusChange) {
        onEpisodeStatusChange(episodeId, newStatus);
      }
    } catch (error) {
      console.error('Fehler beim Aktualisieren des Episode-Status:', error);
    }
  };

  // Öffne den Stream-Link in einem neuen Tab
  const openStreamLink = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (loading) return <p>Lade Episoden...</p>;
  if (error) return <p>Fehler beim Laden der Episoden: {error}</p>;
  if (episodes.length === 0) return <p>Keine Episoden gefunden.</p>;

  return (
    <Table striped hover responsive>
      <thead>
        <tr>
          <th>#</th>
          <th>Titel</th>
          <th>Status</th>
          <th>Verfügbarkeit</th>
          <th>Aktionen</th>
        </tr>
      </thead>
      <tbody>
        {episodes
          .sort((a, b) => a.episoden_nummer - b.episoden_nummer)
          .map(episode => (
            <tr key={episode.id}>
              <td>{episode.episoden_nummer}</td>
              <td>{episode.titel}</td>
              <td>
                <Form.Check
                  type="checkbox"
                  label="Gesehen"
                  checked={episode.status === EpisodeStatus.GESEHEN}
                  onChange={(e) => {
                    const newStatus = e.target.checked 
                      ? EpisodeStatus.GESEHEN 
                      : EpisodeStatus.NICHT_GESEHEN;
                    handleStatusChange(episode.id, newStatus);
                  }}
                />
              </td>
              <td>
                <Badge bg={availabilityVariants[episode.availability_status as EpisodeAvailabilityStatus] || 'secondary'}>
                  {availabilityLabels[episode.availability_status as EpisodeAvailabilityStatus] || episode.availability_status}
                </Badge>
              </td>
              <td>
                {episode.stream_link && (
                  <Button 
                    size="sm" 
                    variant="primary"
                    onClick={() => openStreamLink(episode.stream_link!)}
                  >
                    Stream
                  </Button>
                )}
                {episode.local_file_path && (
                  <Button 
                    size="sm" 
                    variant="success"
                    className="ms-2"
                    onClick={() => alert(`Lokale Datei: ${episode.local_file_path}`)}
                  >
                    Lokal
                  </Button>
                )}
              </td>
            </tr>
          ))}
      </tbody>
    </Table>
  );
};

export default EpisodeList;
