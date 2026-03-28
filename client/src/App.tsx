import './App.css'
import { HealthCheck } from './components/HealthCheck'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>BigCat Technologies</h1>
      </header>

      <main className="app-main">
        <HealthCheck />
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}

export default App
