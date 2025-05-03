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

// Anime Interface - Updated to match backend schema
export interface Anime {
  id: number;
  titel_de: string;
  titel_jp?: string | null;
  titel_org?: string | null;
  titel_en?: string | null;
  synonyme?: string | null;
  status: AnimeStatus;
  beschreibung?: string | null;
  anime_loads_url?: string | null;
  cover_image_url?: string | null;
  cover_local_path?: string | null;
  typ?: string | null;
  jahr?: number | null;
  episoden_anzahl?: string | null;
  laufzeit?: string | null;
  hauptgenre?: string | null;
  nebengenres?: string | null;
  tags?: string | null;
  anisearch_url?: string | null;
  hinzugefuegt_am: string;
  zuletzt_aktualisiert_am: string;
  episoden?: Episode[];
}

// Interface für die Erstellung eines neuen Animes
export interface AnimeCreate {
  titel_de: string;
  titel_jp?: string;
  titel_org?: string;
  titel_en?: string;
  synonyme?: string;
  status?: AnimeStatus;
  beschreibung?: string;
  anime_loads_url?: string;
  cover_image_url?: string;
  typ?: string;
  jahr?: number;
  episoden_anzahl?: string;
  laufzeit?: string;
  hauptgenre?: string;
  nebengenres?: string;
  tags?: string;
  anisearch_url?: string;
}

// Interface für die Aktualisierung eines Animes
export interface AnimeUpdate {
  titel_de?: string;
  titel_jp?: string;
  titel_org?: string;
  titel_en?: string;
  synonyme?: string;
  status?: AnimeStatus;
  beschreibung?: string;
  anime_loads_url?: string;
  cover_image_url?: string;
  typ?: string;
  jahr?: number;
  episoden_anzahl?: string;
  laufzeit?: string;
  hauptgenre?: string;
  nebengenres?: string;
  tags?: string;
  anisearch_url?: string;
}

// Episode Interface
export interface Episode {
  id: number;
  anime_id: number;
  episoden_nummer: number;
  titel: string;
  status: EpisodeStatus;
  availability_status: EpisodeAvailabilityStatus;
  stream_link?: string | null;
  local_file_path?: string | null;
  air_date?: string | null;
  anime_loads_episode_url?: string | null;
  hinzugefuegt_am: string;
  zuletzt_aktualisiert_am: string;
}

// Episode Create Interface
export interface EpisodeCreate {
  anime_id: number;
  episoden_nummer: number;
  titel?: string;
  status?: EpisodeStatus;
  air_date?: string;
  anime_loads_episode_url?: string;
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
