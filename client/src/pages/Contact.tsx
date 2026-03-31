import Nav from '../components/Nav'
import bigcatLogo from '../assets/bigcat_logo.png'
import '../App.css'
import './Contact.css'

export default function Contact() {
  const email = 'samshapiro87.agent@gmail.com'

  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark-group">
          <img src={bigcatLogo} alt="BigCat Technologies logo" className="wordmark-logo" />
          <span className="wordmark">BigCat Technologies</span>
        </div>
        <Nav />
      </header>

      <main className="app-main contact-main">
        <section className="hero">
          <h1>Contact</h1>
          <p className="tagline">Let's talk.</p>
        </section>

        <section className="contact-body">
          <p>
            Have a project in mind? A question about the work? Just want to say hi?
            Drop an email — Sam reads everything.
          </p>
          <a href={`mailto:${email}`} className="contact-email-link">
            {email}
          </a>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
