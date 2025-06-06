import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useThemeStore } from './stores/themeStore'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage'
import HypothesesPage from './pages/HypothesesPage'
import SettingsPage from './pages/SettingsPage'
import ElizaIntegrationPage from './pages/ElizaIntegrationPage'

function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/analysis/:jobId" element={<AnalysisPage />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
        <Route path="/hypotheses" element={<HypothesesPage />} />
        <Route path="/eliza" element={<ElizaIntegrationPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
