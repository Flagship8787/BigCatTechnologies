import Nav from '../components/Nav'
import bigcatLogo from '../assets/bigcat_logo.png'
import '../App.css'
import './Contact.css'

export default function Contact() {
  const email = 'bigcat.mox@gmail.com'

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
            Drop an email.
          </p>
          <a href={`mailto:${email}`} className="contact-email-link">
            {email}
          </a>
        </section>

        <section className="contact-map">
          <h2>Our Home Base</h2>
          <iframe
            title="Brooklyn, NY"
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d96708.34051685308!2d-74.03927096022435!3d40.650002059567516!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c24416947c2109%3A0x82765c7404007886!2sBrooklyn%2C%20NY!5e0!3m2!1sen!2sus!4v1715000000000!5m2!1sen!2sus"
            className="contact-map-iframe"
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
