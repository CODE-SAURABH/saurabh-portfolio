import { Link } from 'react-router-dom'

const year = new Date().getFullYear()

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-row">
        <p>
          © {year} Saurabh Patil <span className="footer-sep">/</span> Designed to keep evolving
        </p>
        <nav className="footer-links" aria-label="Footer">
          <Link to="/projects">Selected work</Link>
          <Link to="/resume">Resume</Link>
          <Link to="/contact">Contact →</Link>
          <a href="#top">Back to top ↑</a>
        </nav>
      </div>
    </footer>
  )
}
