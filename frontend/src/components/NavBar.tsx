import { Navbar, Container, Nav, Form, Button } from 'react-bootstrap';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

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
        <Navbar.Brand href="/">Anime Bibliothek</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/">Startseite</Nav.Link>
            <Nav.Link href="/meine-animes">Meine Animes</Nav.Link>
            <Nav.Link href="/verfügbar">Verfügbar</Nav.Link>
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
