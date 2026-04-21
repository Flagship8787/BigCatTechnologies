import { useMemo } from 'react'
import { useNavigate, useLocation, Outlet } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import { AppProvider, type Navigation } from '@toolpad/core/AppProvider'
import { DashboardLayout } from '@toolpad/core/DashboardLayout'
import DashboardIcon from '@mui/icons-material/Dashboard'
import ArticleIcon from '@mui/icons-material/Article'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import ListIcon from '@mui/icons-material/List'
import AddIcon from '@mui/icons-material/Add'
import { Button, Stack } from '@mui/material'
import { bigcatTheme } from '../../theme'
import bigcatLogo from '../../assets/bigcat_logo.png'

const NAVIGATION: Navigation = [
  {
    segment: 'dashboard',
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
  {
    kind: 'divider',
  },
  {
    segment: 'admin/blogs',
    title: 'Blog',
    icon: <ArticleIcon />,
    children: [
      {
        segment: '',
        title: 'All Blogs',
        icon: <ListIcon />,
        pattern: 'admin/blogs',
      },
      {
        segment: 'new',
        title: 'Create Blog',
        icon: <AddCircleOutlineIcon />,
      },
    ],
  },
]

const BRANDING = {
  title: 'BigCat',
  logo: <img src={bigcatLogo} style={{ height: 26 }} alt="BigCat" />,
}

function DashboardActions() {
  const navigate = useNavigate()
  return (
    <Stack direction="row" spacing={1}>
      <Button
        variant="outlined"
        size="small"
        startIcon={<ArticleIcon />}
        onClick={() => navigate('/admin/blogs')}
      >
        All Blogs
      </Button>
      <Button
        variant="contained"
        size="small"
        startIcon={<AddIcon />}
        onClick={() => navigate('/admin/blogs/new')}
      >
        New Post
      </Button>
    </Stack>
  )
}

interface AdminLayoutProps {
  children?: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth0()

  const router = useMemo(
    () => ({
      pathname: location.pathname,
      searchParams: new URLSearchParams(location.search),
      navigate: (path: string | URL) => navigate(String(path)),
    }),
    [location, navigate],
  )

  const session = user
    ? {
        user: {
          name: user.name ?? user.email ?? 'User',
          email: user.email ?? '',
          image: user.picture,
        },
      }
    : undefined

  return (
    <AppProvider
      navigation={NAVIGATION}
      branding={BRANDING}
      router={router}
      theme={bigcatTheme}
      session={session}
    >
      <DashboardLayout slots={{ toolbarActions: DashboardActions }}>
        {children ?? <Outlet />}
      </DashboardLayout>
    </AppProvider>
  )
}
