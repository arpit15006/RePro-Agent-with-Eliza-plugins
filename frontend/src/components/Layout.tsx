import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Home,
  FileText,
  Network,
  Lightbulb,
  Settings,
  Moon,
  Sun,
  Github,
  ExternalLink,
  Bot
} from 'lucide-react'
import { useThemeStore } from '../stores/themeStore'
import { motion } from 'framer-motion'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()
  const { theme, toggleTheme } = useThemeStore()

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Analysis', href: '/analysis', icon: FileText },
    { name: 'Knowledge Graph', href: '/knowledge-graph', icon: Network },
    { name: 'Hypotheses', href: '/hypotheses', icon: Lightbulb },
    { name: 'Eliza Chat', href: '/eliza', icon: Bot },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">RA</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">RePRO-Agent</h1>
                <p className="text-xs text-muted-foreground">Scientific Reproducibility & AI</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      relative px-3 py-2 rounded-md text-sm font-medium transition-colors
                      ${isActive 
                        ? 'text-primary bg-primary/10' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }
                    `}
                  >
                    <item.icon className="w-4 h-4 inline mr-2" />
                    {item.name}
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute inset-0 bg-primary/10 rounded-md -z-10"
                        initial={false}
                        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                      />
                    )}
                  </Link>
                )
              })}
            </nav>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-md hover:bg-accent transition-colors"
                title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              >
                {theme === 'light' ? (
                  <Moon className="w-4 h-4" />
                ) : (
                  <Sun className="w-4 h-4" />
                )}
              </button>
              
              <a
                href="https://github.com/yourusername/eliza-repro-hypothesis"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-md hover:bg-accent transition-colors"
                title="View on GitHub"
              >
                <Github className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <nav className="md:hidden border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1 py-2 overflow-x-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors
                    ${isActive 
                      ? 'text-primary bg-primary/10' 
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    }
                  `}
                >
                  <item.icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/30 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-3">RePRO-Agent</h3>
              <p className="text-sm text-muted-foreground">
                AI-powered scientific reproducibility assessment and hypothesis generation platform.
              </p>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Manuscript metadata extraction</li>
                <li>• Reproducibility assessment</li>
                <li>• Knowledge graph construction</li>
                <li>• AI hypothesis generation</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-3">Links</h3>
              <div className="space-y-2">
                <a 
                  href="https://github.com/yourusername/eliza-repro-hypothesis"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Github className="w-4 h-4 mr-2" />
                  GitHub Repository
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
                <a 
                  href="https://ai-docs.bio.xyz/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  BioXAI Hackathon
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            </div>
          </div>
          
          <div className="border-t border-border mt-8 pt-6 text-center">
            <p className="text-sm text-muted-foreground">
              © 2024 RePRO-Agent. Built for the BioXAI Hackathon Scientific Outcomes Track.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
