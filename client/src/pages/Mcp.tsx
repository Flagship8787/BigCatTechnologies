import Nav from '../components/Nav'
import bigcatLogo from '../assets/bigcat_logo.png'
import '../App.css'
import './Mcp.css'

export default function Mcp() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark-group">
          <img src={bigcatLogo} alt="BigCat Technologies logo" className="wordmark-logo" />
          <span className="wordmark">BigCat Technologies</span>
        </div>
        <Nav />
      </header>

      <main className="app-main mcp-main">
        <section className="hero">
          <h1>MCP Server</h1>
          <p className="tagline">Model Context Protocol — open your agent to the world.</p>
        </section>

        <section className="mcp-body">
          <h2>What is MCP?</h2>
          <p>
            The <strong>Model Context Protocol</strong> (MCP) is an open standard that lets AI
            assistants connect to external tools and data sources in a structured, secure way.
            Instead of copy-pasting data into a chat window, your AI client talks directly to
            an MCP server — reading context, calling tools, and acting on real-world systems.
          </p>
          <p>
            Think of it as a universal adapter between any LLM and any service you want it to
            interact with.
          </p>

          <h2>Connecting to the BigCat MCP Server</h2>
          <p>
            The BigCat Technologies MCP server is hosted at{' '}
            <code>https://api.bigcattechnologies.com/mcp</code> and supports{' '}
            <strong>Streamable HTTP</strong> transport (the modern MCP transport introduced
            in spec version 2025-03-26).
          </p>

          <h3>Claude Desktop / Claude.ai</h3>
          <p>Add the following to your <code>claude_desktop_config.json</code>:</p>
          <pre className="code-block">{`{
  "mcpServers": {
    "bigcat": {
      "type": "http",
      "url": "https://api.bigcattechnologies.com/mcp"
    }
  }
}`}</pre>

          <h3>OpenClaw / Custom Clients</h3>
          <p>For any MCP client that supports Streamable HTTP, point it at:</p>
          <pre className="code-block">https://api.bigcattechnologies.com/mcp</pre>
          <p>
            No API key is required for public tools. The server uses Server-Sent Events for
            streaming responses and standard HTTP POST for sending messages.
          </p>

          <h3>Testing with curl</h3>
          <p>Send an MCP initialization request:</p>
          <pre className="code-block">{`curl -X POST https://api.bigcattechnologies.com/mcp \\
  -H "Content-Type: application/json" \\
  -H "Accept: text/event-stream" \\
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {},
      "clientInfo": { "name": "curl-test", "version": "1.0" }
    }
  }'`}</pre>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
