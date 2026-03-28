# BigCat Technologies — React Client

A React + TypeScript frontend built with Vite.

## Local Development

1. Copy the env example and set your backend URL:
   ```bash
   cp .env.example .env
   # edit .env and set VITE_API_URL to your backend URL
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the dev server:
   ```bash
   npm run dev
   ```

The app runs at `http://localhost:5173` by default.

## Environment Variables

| Variable       | Default                  | Description                    |
|----------------|--------------------------|--------------------------------|
| `VITE_API_URL` | `http://localhost:3000`  | Base URL for the backend API   |

## Build

```bash
npm run build
```

Output is written to `dist/`.
