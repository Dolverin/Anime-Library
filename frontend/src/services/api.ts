import axios, { AxiosResponse } from 'axios';
import { Anime, Episode, AnimeListResponse, ApiResponse } from '../types';

// API Basis-URL konfigurieren
const API_BASE_URL = 'http://localhost:8000/api';

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
      const response = await api.get<AnimeListResponse>('/animes');
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Einen bestimmten Anime abrufen
  getAnime: async (id: number): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.get<Anime>(`/animes/${id}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Anime nach Titel suchen
  searchAnimes: async (query: string): Promise<ApiResponse<AnimeListResponse>> => {
    try {
      const response = await api.get<AnimeListResponse>(`/animes/search?q=${encodeURIComponent(query)}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Anime-Status aktualisieren
  updateAnimeStatus: async (id: number, status: string): Promise<ApiResponse<Anime>> => {
    try {
      const response = await api.patch<Anime>(`/animes/${id}`, { status });
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  }
};

export const episodeService = {
  // Alle Episoden eines Animes abrufen
  getEpisodesByAnimeId: async (animeId: number): Promise<ApiResponse<Episode[]>> => {
    try {
      const response = await api.get<Episode[]>(`/episodes/anime/${animeId}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Eine bestimmte Episode abrufen
  getEpisode: async (episodeId: number): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.get<Episode>(`/episodes/${episodeId}`);
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Episode-Status aktualisieren
  updateEpisodeStatus: async (episodeId: number, status: string): Promise<ApiResponse<Episode>> => {
    try {
      const response = await api.patch<Episode>(`/episodes/${episodeId}`, { status });
      return createApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  }
};

export default api;
