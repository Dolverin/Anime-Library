import axios, { AxiosResponse } from 'axios';
import { Anime, Episode, AnimeListResponse, ApiResponse, AnimeCreate, AnimeUpdate, EpisodeCreate, ExternalAnimeSearchResult, AnimeScrapingResult } from '../types';

// API Basis-URL konfigurieren
const API_BASE_URL = 'http://localhost:8000';

// Axios-Instance mit Basis-Konfiguration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper-Funktion für API-Responses
const createApiResponse = <T>(response: AxiosResponse<T>): ApiResponse<T> => {
  return {
    data: response.data,
    status: response.status,
  };
};

// Error-Handler
const handleApiError = (error: any): ApiResponse<any> => {
  return {
    error: error.response?.data?.detail || 'Ein Fehler ist aufgetreten',
    status: error.response?.status || 500,
  };
};

// API-Services
export const animeService = {
  // Alle Animes abrufen
  getAllAnimes: async (): Promise<ApiResponse<AnimeListResponse>> => {
    try {
      const response = await api.get<AnimeListResponse>('/api/animes/');
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Einen bestimmten Anime abrufen
  getAnime: async (id: number): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.get<Anime>(`/api/animes/${id}/`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Anime nach Titel suchen
  searchAnimes: async (query: string): Promise<ApiResponse<AnimeListResponse>> => {
    try {
      const response = await api.get<AnimeListResponse>(`/api/animes/search?q=${encodeURIComponent(query)}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Kombinierte Suche (Datenbank + anime-loads.org)
  combinedSearch: async (query: string): Promise<ApiResponse<{
    db_results: Array<{
      id: number;
      titel_de: string;
      titel_jp?: string;
      titel_en?: string;
      titel_org?: string;
      synonyme?: string;
      anime_loads_id?: string;
      anime_loads_url?: string;
      cover_image_url?: string;
      updated_at: Date;
      episodes_count: number;
      latest_episode_update?: Date;
    }>,
    external_results: Array<{
      id: string;
      title: string;
      url: string;
      image_url?: string;
      in_database?: boolean;
      db_id?: number;
      updated_at?: Date;
    }>
  }>> => {
    try {
      const response = await api.get(`/api/animes/combined-search?q=${encodeURIComponent(query)}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Anime-Status aktualisieren
  updateAnimeStatus: async (id: number, status: string): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.patch<Anime>(`/api/animes/${id}/`, { status });
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Einen neuen Anime erstellen
  createAnime: async (animeData: AnimeCreate): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.post<Anime>('/api/animes/', animeData);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Einen vorhandenen Anime aktualisieren
  updateAnime: async (id: number, animeData: AnimeUpdate): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.put<Anime>(`/api/animes/${id}/`, animeData);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  // Externe Anime-Suche auf anime-loads.org
  searchExternalAnime: async (query: string): Promise<ApiResponse<ExternalAnimeSearchResult[]>> => {
    try {
      const response = await api.get<ExternalAnimeSearchResult[]>(`/api/animes/search-external?query=${encodeURIComponent(query)}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  // Scrape einen Anime von anime-loads.org
  scrapeAnimeByUrl: async (url: string): Promise<ApiResponse<AnimeScrapingResult>> => {
    try {
      const response = await api.get<AnimeScrapingResult>(`/api/animes/scrape?url=${encodeURIComponent(url)}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  // Lokale Anime-Dateien scannen und importieren
  scanLocalFiles: async (mediaDir: string): Promise<ApiResponse<{total_files: number, matched_animes: number, updated_episodes: number}>> => {
    try {
      const response = await api.post<{total_files: number, matched_animes: number, updated_episodes: number}>(
        '/api/animes/scan-local-files/', 
        { media_dir: mediaDir }
      );
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Lokale Anime-Dateien scannen und neue Animes erstellen
  scanAndCreateAnimes: async (mediaDir: string): Promise<ApiResponse<{total_files: number, matched_animes: number, updated_episodes: number}>> => {
    try {
      const response = await api.post<{total_files: number, matched_animes: number, updated_episodes: number}>(
        '/api/animes/scan-and-create', 
        { media_dir: mediaDir }
      );
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

export const episodeService = {
  // Alle Episoden eines Animes abrufen
  getEpisodesByAnimeId: async (animeId: number): Promise<ApiResponse<Episode[]>> => {
    try {
      const response = await api.get<Episode[]>(`/api/episodes/${animeId}/`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Eine bestimmte Episode abrufen
  getEpisode: async (animeId: number, episodeId: number): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.get<Episode>(`/api/episodes/${animeId}/${episodeId}/`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Episode-Status aktualisieren
  updateEpisodeStatus: async (episodeId: number, status: string): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.patch<Episode>(`/api/episodes/update/${episodeId}/`, { status });
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Eine neue Episode erstellen
  createEpisode: async (animeId: number, episodeData: EpisodeCreate): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.post<Episode>(`/api/episodes/${animeId}/`, episodeData);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Eine Episode aktualisieren
  updateEpisode: async (episodeId: number, episodeData: Partial<Episode>): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.put<Episode>(`/api/episodes/update/${episodeId}/`, episodeData);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Eine Episode löschen
  deleteEpisode: async (episodeId: number): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.delete<Episode>(`/api/episodes/delete/${episodeId}/`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  }
};

export default api;
