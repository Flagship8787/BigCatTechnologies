import { createTheme } from '@mui/material/styles'

export const bigcatTheme = createTheme({
  palette: {
    primary: {
      main: '#0ea5e9',
      dark: '#0369a1',
      light: '#e0f2fe',
      contrastText: '#fff',
    },
  },
  typography: {
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  shape: {
    borderRadius: 8,
  },
})
