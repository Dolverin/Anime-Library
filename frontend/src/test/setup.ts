/**
 * Test-Setup für die Anime-Bibliothek
 * 
 * Diese Datei konfiguriert die Testumgebung und importiert
 * die notwendigen Erweiterungen für DOM-basierte Tests.
 */

import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Bereinige nach jedem Test automatisch
afterEach(() => {
  cleanup();
});
