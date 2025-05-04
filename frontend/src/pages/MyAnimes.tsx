import { useState, useEffect } from 'react';
import { Container, Row, Col, Spinner, Alert, Form, InputGroup, Button, Pagination, Card, Badge } from 'react-bootstrap';
import { AnimeStatus, Anime } from '../types';
import { animeService } from '../services/api';
import AnimeCard from '../components/AnimeCard';
import { FaSearch, FaThList, FaTh, FaFileImport } from 'react-icons/fa';
import ImportLocalFilesModal from '../components/ImportLocalFilesModal';

// Konstanten für die Pagination
const ITEMS_PER_PAGE = 12;

const MyAnimes = () => {
  const [animes, setAnimes] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter States
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [genreFilter, setGenreFilter] = useState<string>('all');
  const [yearFilter, setYearFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Sortieren State
  const [sortOption, setSortOption] = useState<string>('titel_asc');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState<number>(1);
  
  // Ansichtsmodus: 'card' oder 'list'
  const [viewMode, setViewMode] = useState<'card' | 'list'>('card');
  
  // Liste der einzigartigen Jahre und Genres aus den Animes extrahieren
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [availableGenres, setAvailableGenres] = useState<string[]>([]);
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);

  // Anime Import Modal State
  const [showImportModal, setShowImportModal] = useState<boolean>(false);

  useEffect(() => {
    const fetchAnimes = async () => {
      setLoading(true);
      const response = await animeService.getAllAnimes();
      
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        const loadedAnimes = response.data.items || [];
        setAnimes(loadedAnimes);
        
        // Einzigartige Jahre, Genres und Typen extrahieren
        const years = loadedAnimes
          .map(anime => anime.jahr)
          .filter((jahr): jahr is number => jahr !== null && jahr !== undefined);
        setAvailableYears([...new Set(years)].sort((a, b) => b - a));
        
        const genres = loadedAnimes
          .flatMap(anime => {
            const hauptgenre = anime.hauptgenre ? [anime.hauptgenre] : [];
            const nebengenres = anime.nebengenres ? anime.nebengenres.split(',').map(g => g.trim()) : [];
            return [...hauptgenre, ...nebengenres];
          })
          .filter(genre => genre && genre.length > 0);
        setAvailableGenres([...new Set(genres)].sort());
        
        const types = loadedAnimes
          .map(anime => anime.typ)
          .filter((typ): typ is string => typ !== null && typ !== undefined);
        setAvailableTypes([...new Set(types)].sort());
      }
      
      setLoading(false);
    };

    fetchAnimes();
  }, []);

  // Filtern der Animes basierend auf allen Filtern
  const filteredAnimes = animes.filter(anime => {
    // Status-Filter
    if (statusFilter !== 'all' && anime.status !== statusFilter) {
      return false;
    }
    
    // Genre-Filter
    if (genreFilter !== 'all') {
      const hauptgenre = anime.hauptgenre || '';
      const nebengenres = anime.nebengenres || '';
      if (!hauptgenre.includes(genreFilter) && !nebengenres.includes(genreFilter)) {
        return false;
      }
    }
    
    // Jahr-Filter
    if (yearFilter !== 'all' && anime.jahr !== parseInt(yearFilter)) {
      return false;
    }
    
    // Typ-Filter
    if (typeFilter !== 'all' && anime.typ !== typeFilter) {
      return false;
    }
    
    // Suche
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const titel_de = (anime.titel_de || '').toLowerCase();
      const titel_en = (anime.titel_en || '').toLowerCase();
      const titel_jp = (anime.titel_jp || '').toLowerCase();
      
      if (!titel_de.includes(query) && !titel_en.includes(query) && !titel_jp.includes(query)) {
        return false;
      }
    }
    
    return true;
  });

  // Sortieren der gefilterten Animes
  const sortedAnimes = [...filteredAnimes].sort((a, b) => {
    switch (sortOption) {
      case 'titel_asc':
        return a.titel_de.localeCompare(b.titel_de);
      case 'titel_desc':
        return b.titel_de.localeCompare(a.titel_de);
      case 'jahr_asc':
        return (a.jahr || 0) - (b.jahr || 0);
      case 'jahr_desc':
        return (b.jahr || 0) - (a.jahr || 0);
      case 'hinzugefuegt_asc':
        return new Date(a.hinzugefuegt_am).getTime() - new Date(b.hinzugefuegt_am).getTime();
      case 'hinzugefuegt_desc':
        return new Date(b.hinzugefuegt_am).getTime() - new Date(a.hinzugefuegt_am).getTime();
      default:
        return 0;
    }
  });

  // Pagination - Aktuelle Seite von Animes
  const totalPages = Math.ceil(sortedAnimes.length / ITEMS_PER_PAGE);
  const indexOfLastAnime = currentPage * ITEMS_PER_PAGE;
  const indexOfFirstAnime = indexOfLastAnime - ITEMS_PER_PAGE;
  const currentAnimes = sortedAnimes.slice(indexOfFirstAnime, indexOfLastAnime);

  // Pagination-Komponente erstellen
  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const items = [];
    
    // Vorherige Seite
    items.push(
      <Pagination.Prev 
        key="prev" 
        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
        disabled={currentPage === 1}
      />
    );

    // Erste Seite immer anzeigen
    items.push(
      <Pagination.Item 
        key={1} 
        active={currentPage === 1}
        onClick={() => setCurrentPage(1)}
      >
        1
      </Pagination.Item>
    );

    // Ellipsis hinzufügen, wenn nötig
    if (currentPage > 3) {
      items.push(<Pagination.Ellipsis key="ellipsis1" />);
    }

    // Mittlere Seiten anzeigen
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      if (i > 1 && i < totalPages) {
        items.push(
          <Pagination.Item 
            key={i} 
            active={currentPage === i}
            onClick={() => setCurrentPage(i)}
          >
            {i}
          </Pagination.Item>
        );
      }
    }

    // Ellipsis hinzufügen, wenn nötig
    if (currentPage < totalPages - 2) {
      items.push(<Pagination.Ellipsis key="ellipsis2" />);
    }

    // Letzte Seite immer anzeigen, wenn es mehr als eine Seite gibt
    if (totalPages > 1) {
      items.push(
        <Pagination.Item 
          key={totalPages} 
          active={currentPage === totalPages}
          onClick={() => setCurrentPage(totalPages)}
        >
          {totalPages}
        </Pagination.Item>
      );
    }

    // Nächste Seite
    items.push(
      <Pagination.Next 
        key="next" 
        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
        disabled={currentPage === totalPages}
      />
    );

    return <Pagination className="justify-content-center mt-4">{items}</Pagination>;
  };

  // Filter zurücksetzen
  const resetFilters = () => {
    setStatusFilter('all');
    setGenreFilter('all');
    setYearFilter('all');
    setTypeFilter('all');
    setSearchQuery('');
    setSortOption('titel_asc');
    setCurrentPage(1);
  };

  // Import-Erfolgshandler - wird aufgerufen, wenn der Import erfolgreich war
  const handleImportSuccess = async () => {
    // Neu laden der Animes
    setLoading(true);
    const response = await animeService.getAllAnimes();
    
    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      const loadedAnimes = response.data.items || [];
      setAnimes(loadedAnimes);
    }
    
    setLoading(false);
  };

  // Render-Funktion für Listenansicht
  const renderListView = () => {
    return (
      <div className="list-view mt-3">
        <div className="list-header bg-light p-2 d-flex border-top border-bottom">
          <div className="col-5 fw-bold">Titel</div>
          <div className="col-2 fw-bold">Typ</div>
          <div className="col-1 fw-bold">Jahr</div>
          <div className="col-2 fw-bold">Status</div>
          <div className="col-2 fw-bold">Episoden</div>
        </div>
        {currentAnimes.map(anime => (
          <div 
            key={anime.id} 
            className="list-item d-flex p-2 border-bottom align-items-center hover-bg-light"
            onClick={() => window.location.href = `/anime/${anime.id}`}
            style={{ cursor: 'pointer' }}
          >
            <div className="col-5">{anime.titel_de}</div>
            <div className="col-2">{anime.typ || '-'}</div>
            <div className="col-1">{anime.jahr || '-'}</div>
            <div className="col-2">
              <Badge 
                bg={statusVariants[anime.status as AnimeStatus] || 'secondary'}
                className="mb-0"
              >
                {statusLabels[anime.status as AnimeStatus] || anime.status}
              </Badge>
            </div>
            <div className="col-2">{anime.episoden?.length || 0}</div>
          </div>
        ))}
      </div>
    );
  };

  // Status-Übersetzungen und Farben
  const statusLabels: Record<AnimeStatus, string> = {
    [AnimeStatus.PLAN_TO_WATCH]: 'Geplant',
    [AnimeStatus.WATCHING]: 'Schaue ich',
    [AnimeStatus.COMPLETED]: 'Abgeschlossen',
    [AnimeStatus.ON_HOLD]: 'Pausiert',
    [AnimeStatus.DROPPED]: 'Abgebrochen'
  };

  const statusVariants: Record<AnimeStatus, string> = {
    [AnimeStatus.PLAN_TO_WATCH]: 'info',
    [AnimeStatus.WATCHING]: 'primary',
    [AnimeStatus.COMPLETED]: 'success',
    [AnimeStatus.ON_HOLD]: 'warning',
    [AnimeStatus.DROPPED]: 'danger'
  };

  return (
    <Container>
      <Row className="mb-4 align-items-center">
        <Col>
          <h1>Meine Anime-Sammlung</h1>
        </Col>
        <Col xs="auto">
          <Button 
            variant="success" 
            className="me-2"
            onClick={() => setShowImportModal(true)}
          >
            <FaFileImport className="me-2" /> Anime Importieren
          </Button>
        </Col>
      </Row>
      
      {/* Import Modal */}
      <ImportLocalFilesModal
        show={showImportModal}
        onHide={() => setShowImportModal(false)}
        onSuccess={handleImportSuccess}
      />
      
      {/* Filter-Cards mit Collapse */}
      <Card className="mb-4 filter-card">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Filter & Sortierung</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            {/* Suchfeld */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Suche:</Form.Label>
                <InputGroup>
                  <Form.Control
                    type="text"
                    placeholder="Nach Titel suchen..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1); // Zurück zur ersten Seite bei Suche
                    }}
                  />
                  <Button variant="outline-secondary">
                    <FaSearch />
                  </Button>
                </InputGroup>
              </Form.Group>
            </Col>

            {/* Status-Filter */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Status:</Form.Label>
                <Form.Select 
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setCurrentPage(1); // Zurück zur ersten Seite bei Filteränderung
                  }}
                >
                  <option value="all">Alle Status</option>
                  <option value={AnimeStatus.WATCHING}>Schaue ich</option>
                  <option value={AnimeStatus.COMPLETED}>Abgeschlossen</option>
                  <option value={AnimeStatus.PLAN_TO_WATCH}>Geplant</option>
                  <option value={AnimeStatus.ON_HOLD}>Pausiert</option>
                  <option value={AnimeStatus.DROPPED}>Abgebrochen</option>
                </Form.Select>
              </Form.Group>
            </Col>

            {/* Genre-Filter */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Genre:</Form.Label>
                <Form.Select 
                  value={genreFilter}
                  onChange={(e) => {
                    setGenreFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                >
                  <option value="all">Alle Genres</option>
                  {availableGenres.map(genre => (
                    <option key={genre} value={genre}>{genre}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            {/* Jahr-Filter */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Jahr:</Form.Label>
                <Form.Select 
                  value={yearFilter}
                  onChange={(e) => {
                    setYearFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                >
                  <option value="all">Alle Jahre</option>
                  {availableYears.map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            {/* Typ-Filter */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Typ:</Form.Label>
                <Form.Select 
                  value={typeFilter}
                  onChange={(e) => {
                    setTypeFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                >
                  <option value="all">Alle Typen</option>
                  {availableTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            {/* Sortierung */}
            <Col md={6} lg={4} className="mb-3">
              <Form.Group>
                <Form.Label>Sortieren nach:</Form.Label>
                <Form.Select 
                  value={sortOption}
                  onChange={(e) => setSortOption(e.target.value)}
                >
                  <option value="titel_asc">Titel (A-Z)</option>
                  <option value="titel_desc">Titel (Z-A)</option>
                  <option value="jahr_asc">Jahr (Aufsteigend)</option>
                  <option value="jahr_desc">Jahr (Absteigend)</option>
                  <option value="hinzugefuegt_asc">Hinzugefügt (Älteste zuerst)</option>
                  <option value="hinzugefuegt_desc">Hinzugefügt (Neueste zuerst)</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <div className="d-flex justify-content-between mt-2">
            {/* Filter zurücksetzen */}
            <Button 
              variant="outline-secondary" 
              size="sm"
              onClick={resetFilters}
            >
              Filter zurücksetzen
            </Button>
            
            {/* Ansichtswechsel Buttons */}
            <div className="view-mode-toggle">
              <Button 
                variant={viewMode === 'card' ? 'primary' : 'outline-primary'} 
                className="me-2"
                onClick={() => setViewMode('card')}
              >
                <FaTh /> Karten
              </Button>
              <Button 
                variant={viewMode === 'list' ? 'primary' : 'outline-primary'} 
                onClick={() => setViewMode('list')}
              >
                <FaThList /> Liste
              </Button>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Lade-Indikator */}
      {loading && (
        <div className="text-center my-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Lade Animes...</p>
        </div>
      )}

      {/* Fehlermeldung */}
      {error && (
        <Alert variant="danger">
          Fehler beim Laden der Daten: {error}
        </Alert>
      )}

      {/* Keine Anime-Nachricht */}
      {!loading && !error && filteredAnimes.length === 0 && (
        <Alert variant="info">
          Keine Animes gefunden. Füge neue Animes hinzu oder ändere den Filter.
        </Alert>
      )}

      {/* Ergebnis-Zusammenfassung */}
      {!loading && !error && filteredAnimes.length > 0 && (
        <div className="d-flex justify-content-between align-items-center mb-3">
          <p className="mb-0">
            {filteredAnimes.length} Anime(s) gefunden 
            {statusFilter !== 'all' && ` mit Status "${statusLabels[statusFilter as AnimeStatus] || statusFilter}"`}
            {genreFilter !== 'all' && ` im Genre "${genreFilter}"`}
            {yearFilter !== 'all' && ` aus dem Jahr ${yearFilter}`}
            {typeFilter !== 'all' && ` vom Typ "${typeFilter}"`}
            {searchQuery && ` passend zu "${searchQuery}"`}
          </p>
        </div>
      )}

      {/* Anime-Anzeige (Karten oder Liste) */}
      {!loading && !error && currentAnimes.length > 0 && (
        <>
          {viewMode === 'card' ? (
            <Row xs={1} sm={2} md={3} lg={4} className="g-4">
              {currentAnimes.map(anime => (
                <Col key={anime.id}>
                  <AnimeCard anime={anime} />
                </Col>
              ))}
            </Row>
          ) : (
            renderListView()
          )}
          
          {/* Pagination */}
          {renderPagination()}
        </>
      )}
    </Container>
  );
};

export default MyAnimes;
