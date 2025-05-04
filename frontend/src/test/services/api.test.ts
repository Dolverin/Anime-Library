/**
 * Tests für die API-Services
 * 
 * Diese Tests überprüfen die korrekten API-Aufrufe mit MSW als Mock-Server.
 */
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { animeService, episodeService } from '../../services/api';
import { Anime, Episode, AnimeStatus, EpisodeStatus } from '../../types';

// Mock-Daten für die Tests
const mockAnimes: Partial<Anime>[] = [
  { id: 1, titel_de: 'Test Anime 1', jahr: 2021, status: AnimeStatus.PLAN_TO_WATCH, typ: 'TV' },
  { id: 2, titel_de: 'Test Anime 2', jahr: 2022, status: AnimeStatus.WATCHING, typ: 'Film' }
];

const mockEpisodes: Partial<Episode>[] = [
  { id: 1, anime_id: 1, episoden_nummer: 1, titel: 'Episode 1', status: EpisodeStatus.NICHT_GESEHEN },
  { id: 2, anime_id: 1, episoden_nummer: 2, titel: 'Episode 2', status: EpisodeStatus.GESEHEN }
];

// MSW Server-Setup für API-Mocks
const server = setupServer(
  // Animes Endpunkte
  http.get('http://192.168.178.40:8000/api/animes', () => {
    return HttpResponse.json({ 
      items: mockAnimes,
      total: mockAnimes.length 
    });
  }),
  
  http.get('http://192.168.178.40:8000/api/animes/1', () => {
    return HttpResponse.json(mockAnimes[0]);
  }),
  
  // Episoden Endpunkte
  http.get('http://192.168.178.40:8000/api/episodes/1', () => {
    return HttpResponse.json(mockEpisodes);
  }),
  
  http.patch('http://192.168.178.40:8000/api/episodes/1', () => {
    return HttpResponse.json({ 
      ...mockEpisodes[0], 
      status: EpisodeStatus.GESEHEN,
    });
  }),
  
  // Error-Fall
  http.get('http://192.168.178.40:8000/api/animes/999', () => {
    return HttpResponse.json(
      { detail: 'Anime nicht gefunden' },
      { status: 404 }
    );
  })
);

// Server starten/stoppen vor/nach allen Tests
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Anime Service', () => {
  it('sollte alle Animes korrekt abrufen', async () => {
    const response = await animeService.getAllAnimes();
    
    expect(response.status).toBe(200);
    expect(response.data?.items).toHaveLength(2);
    expect(response.data?.items[0].titel_de).toBe('Test Anime 1');
  });
  
  it('sollte einen bestimmten Anime nach ID abrufen', async () => {
    const response = await animeService.getAnime(1);
    
    expect(response.status).toBe(200);
    expect(response.data?.titel_de).toBe('Test Anime 1');
  });
  
  it('sollte einen Fehler zurückgeben, wenn der API-Aufruf fehlschlägt', async () => {
    const response = await animeService.getAnime(999);
    
    expect(response.status).toBe(404);
    expect(response.error).toBe('Anime nicht gefunden');
  });
});

describe('Episode Service', () => {
  it('sollte alle Episoden eines Animes abrufen', async () => {
    const response = await episodeService.getEpisodesByAnimeId(1);
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveLength(2);
    expect(response.data?.[0].titel).toBe('Episode 1');
  });
  
  it('sollte den Status einer Episode aktualisieren', async () => {
    const response = await episodeService.updateEpisodeStatus(1, EpisodeStatus.GESEHEN);
    
    expect(response.status).toBe(200);
    expect(response.data?.status).toBe(EpisodeStatus.GESEHEN);
  });
});
