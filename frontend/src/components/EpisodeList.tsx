import { Badge, Button, Spinner, Alert } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import { Episode, EpisodeStatus, EpisodeAvailabilityStatus } from '../types';
import { episodeService } from '../services/api';
import { FaCheck, FaEdit, FaTrashAlt, FaPlay, FaFolder, FaEye, FaEyeSlash, FaExternalLinkAlt } from 'react-icons/fa';

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
  onDeleteEpisode?: (episodeId: number) => void;
}

const EpisodeList: React.FC<EpisodeListProps> = ({ 
  animeId, 
  episodes: propEpisodes,
  onEpisodeStatusChange,
  onDeleteEpisode
}) => {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingEpisodeIds, setProcessingEpisodeIds] = useState<number[]>([]);

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
      // Speicher den aktuellen Verarbeitungsstatus
      setProcessingEpisodeIds(prev => [...prev, episodeId]);
      
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
    } finally {
      // Entferne Episode aus der Verarbeitungsliste
      setProcessingEpisodeIds(prev => prev.filter(id => id !== episodeId));
    }
  };

  // Öffne den Stream-Link in einem neuen Tab
  const openStreamLink = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  // Episode löschen mit Bestätigung
  const handleDeleteEpisode = (episode: Episode) => {
    if (window.confirm(`Möchtest du Episode ${episode.episoden_nummer}: "${episode.titel}" wirklich löschen?`)) {
      onDeleteEpisode?.(episode.id);
    }
  };

  if (loading) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" variant="primary" />
        <p className="mt-2">Lade Episoden...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert variant="danger">
        Fehler beim Laden der Episoden: {error}
      </Alert>
    );
  }
  
  if (episodes.length === 0) {
    return (
      <Alert variant="info">
        Keine Episoden gefunden.
      </Alert>
    );
  }

  return (
    <div className="episode-table-container">
      <table className="episode-table">
        <thead>
          <tr>
            <th style={{ width: '5%' }}>#</th>
            <th style={{ width: '40%' }}>Titel</th>
            <th style={{ width: '15%' }}>Status</th>
            <th style={{ width: '20%' }}>Verfügbarkeit</th>
            <th style={{ width: '20%' }}>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          {episodes
            .sort((a, b) => a.episoden_nummer - b.episoden_nummer)
            .map(episode => {
              const isProcessing = processingEpisodeIds.includes(episode.id);
              const rowClassName = episode.status === EpisodeStatus.GESEHEN ? 'episode-row-watched' : '';
              
              return (
                <tr key={episode.id} className={rowClassName}>
                  <td>{episode.episoden_nummer}</td>
                  <td>
                    <div className="d-flex align-items-center">
                      {episode.status === EpisodeStatus.GESEHEN && (
                        <span className="me-2 text-success">
                          <FaCheck />
                        </span>
                      )}
                      <span>{episode.titel}</span>
                    </div>
                    {episode.air_date && (
                      <small className="text-muted d-block">
                        Ausgestrahlt: {new Date(episode.air_date).toLocaleDateString()}
                      </small>
                    )}
                  </td>
                  <td>
                    <Button
                      variant={episode.status === EpisodeStatus.GESEHEN ? "success" : "outline-secondary"}
                      size="sm"
                      className="d-flex align-items-center"
                      onClick={() => {
                        const newStatus = episode.status === EpisodeStatus.GESEHEN
                          ? EpisodeStatus.NICHT_GESEHEN
                          : EpisodeStatus.GESEHEN;
                        handleStatusChange(episode.id, newStatus);
                      }}
                      disabled={isProcessing}
                    >
                      {isProcessing ? (
                        <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                      ) : episode.status === EpisodeStatus.GESEHEN ? (
                        <><FaEye className="me-1" /> Gesehen</>
                      ) : (
                        <><FaEyeSlash className="me-1" /> Nicht gesehen</>
                      )}
                    </Button>
                  </td>
                  <td>
                    <Badge 
                      bg={availabilityVariants[episode.availability_status as EpisodeAvailabilityStatus] || 'secondary'}
                      className="py-2 px-3"
                    >
                      {availabilityLabels[episode.availability_status as EpisodeAvailabilityStatus] || episode.availability_status}
                    </Badge>
                  </td>
                  <td>
                    <div className="episode-action-icons">
                      {episode.stream_link && (
                        <Button 
                          size="sm" 
                          variant="outline-primary"
                          title="Stream ansehen"
                          onClick={() => openStreamLink(episode.stream_link!)}
                        >
                          <FaPlay />
                        </Button>
                      )}
                      {episode.local_file_path && (
                        <Button 
                          size="sm" 
                          variant="outline-success"
                          title={`Lokale Datei: ${episode.local_file_path}`}
                          onClick={() => alert(`Lokale Datei: ${episode.local_file_path}`)}
                        >
                          <FaFolder />
                        </Button>
                      )}
                      {episode.anime_loads_episode_url && (
                        <Button
                          size="sm"
                          variant="outline-info"
                          title="Auf Anime-Loads ansehen"
                          onClick={() => openStreamLink(episode.anime_loads_episode_url!)}
                        >
                          <FaExternalLinkAlt />
                        </Button>
                      )}
                      <Button 
                        size="sm" 
                        variant="outline-secondary"
                        title="Episode bearbeiten"
                        onClick={() => window.location.href = `/anime/${animeId}/episode/${episode.id}/bearbeiten`}
                      >
                        <FaEdit />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline-danger"
                        title="Episode löschen"
                        onClick={() => handleDeleteEpisode(episode)}
                      >
                        <FaTrashAlt />
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
};

export default EpisodeList;
