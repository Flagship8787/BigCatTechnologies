import { useMemo } from 'react'
import { useNavigate, useLocation, Outlet } from 'react-router-dom'
import { AppProvider, type Navigation } from '@toolpad/core/AppProvider'
import { DashboardLayout } from '@toolpad/core/DashboardLayout'
import DashboardIcon from '@mui/icons-material/Dashboard'
import ArticleIcon from '@mui/icons-material/Article'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import ListIcon from '@mui/icons-material/List'

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
  title: 'BigCat Technologies',
}

interface AdminLayoutProps {
  children?: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()

  const router = useMemo(
    () => ({
      pathname: location.pathname,
      searchParams: new URLSearchParams(location.search),
      navigate: (path: string | URL) => navigate(String(path)),
    }),
    [location, navigate],
  )

  return (
    <AppProvider navigation={NAVIGATION} branding={BRANDING} router={router}>
      <DashboardLayout>
        {children ?? <Outlet />}
      </DashboardLayout>
    </AppProvider>
  )
}
