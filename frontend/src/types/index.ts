// Typdefinitionen für die Anime-Library

// Anime-Status Enum (sollte mit Backend übereinstimmen)
export enum AnimeStatus {
  PLAN_TO_WATCH = "plan_to_watch",
  WATCHING = "watching",
  COMPLETED = "completed",
  ON_HOLD = "on_hold",
  DROPPED = "dropped"
}

// Episode Status Enum
export enum EpisodeStatus {
  NICHT_GESEHEN = "nicht_gesehen",
  GESEHEN = "gesehen"
}

// Episoden-Verfügbarkeitsstatus
export enum EpisodeAvailabilityStatus {
  NOT_AVAILABLE = "not_available",
  AVAILABLE_ONLINE = "available_online",
  OWNED = "owned",
  OWNED_AND_AVAILABLE_ONLINE = "owned_and_available_online"
}

// Anime Interface
export interface Anime {
  id: number;
  titel: string;
  status: AnimeStatus;
  beschreibung: string;
  anime_loads_url: string;
  cover_image_url: string | null;
  cover_local_path: string | null;
  erstellungsdatum: string;
  aktualisierungsdatum: string;
  title_variants?: string[];
  episodes?: Episode[];
}

// Episode Interface
export interface Episode {
  id: number;
  anime_id: number;
  episoden_nummer: number;
  titel: string;
  status: EpisodeStatus;
  availability_status: EpisodeAvailabilityStatus;
  stream_link: string | null;
  local_file_path: string | null;
  air_date: string | null;
  anime_loads_episode_url: string | null;
  erstellungsdatum: string;
  aktualisierungsdatum: string;
}

// API Response Interfaces
export interface AnimeListResponse {
  items: Anime[];
  total: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}
