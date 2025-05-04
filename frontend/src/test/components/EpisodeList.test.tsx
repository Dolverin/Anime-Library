/**
 * Tests für die EpisodeList-Komponente
 * 
 * Dieser Test überprüft, ob die EpisodeList-Komponente korrekt rendert
 * und auf Benutzerinteraktionen reagiert.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EpisodeList from '../../components/EpisodeList';
import { Episode, EpisodeStatus, EpisodeAvailabilityStatus } from '../../types';

// Mock-Daten für die Tests
const mockEpisodes: Partial<Episode>[] = [
  { 
    id: 1, 
    anime_id: 1, 
    episoden_nummer: 1, 
    titel: 'Episode 1', 
    status: EpisodeStatus.NICHT_GESEHEN,
    availability_status: EpisodeAvailabilityStatus.AVAILABLE_ONLINE,
    hinzugefuegt_am: '2025-01-01',
    zuletzt_aktualisiert_am: '2025-01-01'
  },
  { 
    id: 2, 
    anime_id: 1, 
    episoden_nummer: 2, 
    titel: 'Episode 2', 
    status: EpisodeStatus.GESEHEN,
    availability_status: EpisodeAvailabilityStatus.OWNED,
    hinzugefuegt_am: '2025-01-01',
    zuletzt_aktualisiert_am: '2025-01-01'
  }
];

// Mock-Funktionen für die Callbacks
const mockEpisodeStatusChange = vi.fn();
const mockDeleteEpisode = vi.fn();

describe('EpisodeList Komponente', () => {
  beforeEach(() => {
    // Setze Mock-Funktionen vor jedem Test zurück
    vi.clearAllMocks();
  });

  it('sollte korrekt rendern mit Episodendaten', () => {
    render(
      <EpisodeList 
        animeId={1}
        episodes={mockEpisodes as Episode[]} 
        onEpisodeStatusChange={mockEpisodeStatusChange} 
        onDeleteEpisode={mockDeleteEpisode}
      />
    );
    
    // Überprüfe, ob Episoden angezeigt werden
    expect(screen.getByText('Episode 1')).toBeInTheDocument();
    expect(screen.getByText('Episode 2')).toBeInTheDocument();
    
    // Überprüfe, ob die Episodennummern angezeigt werden
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('sollte eine Ladeanzeige anzeigen, wenn keine Episoden übergeben werden und intern geladen wird', () => {
    render(
      <EpisodeList 
        animeId={1}
        onEpisodeStatusChange={mockEpisodeStatusChange} 
        onDeleteEpisode={mockDeleteEpisode}
      />
    );
    
    // Überprüfe, ob die Ladeanzeige angezeigt wird
    expect(screen.getByText(/Lade Episoden/i)).toBeInTheDocument();
  });

  it('sollte eine Meldung anzeigen, wenn keine Episoden vorhanden sind', () => {
    render(
      <EpisodeList 
        animeId={1}
        episodes={[]} 
        onEpisodeStatusChange={mockEpisodeStatusChange}
        onDeleteEpisode={mockDeleteEpisode}
      />
    );
    
    // Überprüfe, ob die "Keine Episoden"-Meldung angezeigt wird
    expect(screen.getByText(/Keine Episoden gefunden/i)).toBeInTheDocument();
  });
  
  // Weitere Tests können für Benutzerinteraktionen hinzugefügt werden
  // Zum Beispiel:
  // - Test für "Als gesehen markieren" Funktion
  // - Test für "Episode löschen" Funktion
});
