import { Navbar, Container, Nav, Form, Button } from 'react-bootstrap';
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const NavBar = () => {
  const [suchBegriff, setSuchBegriff] = useState('');
  const navigate = useNavigate();

  const handleSuche = (e: React.FormEvent) => {
    e.preventDefault();
    if (suchBegriff.trim()) {
      navigate(`/suche?q=${encodeURIComponent(suchBegriff.trim())}`);
    }
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Link to="/" className="navbar-brand">Anime Bibliothek</Link>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Link to="/" className="nav-link custom-nav-link">Startseite</Link>
            <Link to="/meine-animes" className="nav-link custom-nav-link">Meine Animes</Link>
            <Link to="/verfügbar" className="nav-link custom-nav-link">Verfügbar</Link>
            <Link to="/anime-hinzufuegen" className="nav-link custom-nav-link">Anime hinzufügen</Link>
            <Link to="/anime-loads-suche" className="nav-link custom-nav-link">
              <i className="bi bi-search me-1"></i>
              Anime-Loads Suche
            </Link>
          </Nav>
          <Form className="d-flex" onSubmit={handleSuche}>
            <Form.Control
              type="search"
              placeholder="Anime suchen..."
              className="me-2"
              aria-label="Suchen"
              value={suchBegriff}
              onChange={(e) => setSuchBegriff(e.target.value)}
            />
            <Button variant="outline-light" type="submit">Suchen</Button>
          </Form>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default NavBar;
