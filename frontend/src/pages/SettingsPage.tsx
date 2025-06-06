import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Moon, 
  Sun, 
  Save, 
  RefreshCw, 
  Key, 
  Database,
  Bell,
  Shield,
  Info,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { useThemeStore } from '../stores/themeStore'
import { apiService } from '../services/api'
import toast from 'react-hot-toast'

const SettingsPage = () => {
  const { theme, toggleTheme } = useThemeStore()
  const [settings, setSettings] = useState({
    apiKeys: {
      openai: '',
      anthropic: '',
      gemini: ''
    },
    preferences: {
      defaultModel: 'gemini-pro',
      defaultHypotheses: 5,
      autoRefresh: true,
      notifications: true
    },
    analysis: {
      timeout: 300,
      maxFileSize: 50,
      enableDocker: true
    }
  })
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'connected' | 'error'>('unknown')

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('repro-agent-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings(prev => ({ ...prev, ...parsed }))
      } catch (error) {
        console.error('Error loading settings:', error)
      }
    }
    
    // Test API connection
    testApiConnection()
  }, [])

  const testApiConnection = async () => {
    setTesting(true)
    try {
      await apiService.healthCheck()
      setApiStatus('connected')
    } catch (error) {
      setApiStatus('error')
    } finally {
      setTesting(false)
    }
  }

  const saveSettings = () => {
    setSaving(true)
    try {
      localStorage.setItem('repro-agent-settings', JSON.stringify(settings))
      toast.success('Settings saved successfully!')
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const resetSettings = () => {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      localStorage.removeItem('repro-agent-settings')
      setSettings({
        apiKeys: {
          openai: '',
          anthropic: '',
          gemini: ''
        },
        preferences: {
          defaultModel: 'gemini-pro',
          defaultHypotheses: 5,
          autoRefresh: true,
          notifications: true
        },
        analysis: {
          timeout: 300,
          maxFileSize: 50,
          enableDocker: true
        }
      })
      toast.success('Settings reset to defaults')
    }
  }

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value
      }
    }))
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">
            Configure your RePRO-Agent preferences and API settings
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={resetSettings}
            className="border border-border px-4 py-2 rounded-lg font-medium hover:bg-accent transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Reset
          </button>
          
          <button
            onClick={saveSettings}
            disabled={saving}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* API Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-muted-foreground" />
            <h3 className="text-lg font-semibold text-foreground">API Connection</h3>
          </div>
          
          <button
            onClick={testApiConnection}
            disabled={testing}
            className="flex items-center gap-2 px-3 py-1 text-sm border border-border rounded-md hover:bg-accent transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${testing ? 'animate-spin' : ''}`} />
            Test Connection
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          {apiStatus === 'connected' && (
            <>
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-500">Connected to backend API</span>
            </>
          )}
          {apiStatus === 'error' && (
            <>
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-500">Cannot connect to backend API</span>
            </>
          )}
          {apiStatus === 'unknown' && (
            <>
              <RefreshCw className="w-5 h-5 text-yellow-500 animate-spin" />
              <span className="text-yellow-500">Testing connection...</span>
            </>
          )}
        </div>
      </motion.div>

      {/* Theme Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          {theme === 'light' ? (
            <Sun className="w-5 h-5 text-muted-foreground" />
          ) : (
            <Moon className="w-5 h-5 text-muted-foreground" />
          )}
          <h3 className="text-lg font-semibold text-foreground">Appearance</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-foreground">Theme</label>
              <p className="text-xs text-muted-foreground">Choose your preferred color scheme</p>
            </div>
            <button
              onClick={toggleTheme}
              className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-accent transition-colors"
            >
              {theme === 'light' ? (
                <>
                  <Moon className="w-4 h-4" />
                  Switch to Dark
                </>
              ) : (
                <>
                  <Sun className="w-4 h-4" />
                  Switch to Light
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>

      {/* API Keys */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Key className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">API Keys</h3>
        </div>
        
        <div className="space-y-4">
          <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Info className="w-5 h-5 text-blue-500 mt-0.5" />
              <div className="text-sm">
                <p className="text-blue-700 dark:text-blue-300 font-medium mb-1">
                  API keys are stored locally in your browser
                </p>
                <p className="text-blue-600 dark:text-blue-400">
                  Your keys are never sent to our servers and remain private to your session.
                </p>
              </div>
            </div>
          </div>
          
          {[
            { key: 'gemini', label: 'Google Gemini API Key', placeholder: 'AIza...' },
            { key: 'openai', label: 'OpenAI API Key', placeholder: 'sk-...' },
            { key: 'anthropic', label: 'Anthropic API Key', placeholder: 'sk-ant-...' }
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-foreground mb-2">
                {label}
              </label>
              <input
                type="password"
                value={settings.apiKeys[key as keyof typeof settings.apiKeys]}
                onChange={(e) => updateSetting('apiKeys', key, e.target.value)}
                placeholder={placeholder}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          ))}
        </div>
      </motion.div>

      {/* Analysis Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">Analysis Preferences</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Default LLM Model
            </label>
            <select
              value={settings.preferences.defaultModel}
              onChange={(e) => updateSetting('preferences', 'defaultModel', e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="gemini-pro">Gemini Pro</option>
              <option value="gpt-4">GPT-4</option>
              <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Default Number of Hypotheses
            </label>
            <select
              value={settings.preferences.defaultHypotheses}
              onChange={(e) => updateSetting('preferences', 'defaultHypotheses', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value={3}>3 hypotheses</option>
              <option value={5}>5 hypotheses</option>
              <option value={7}>7 hypotheses</option>
              <option value={10}>10 hypotheses</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Analysis Timeout (seconds)
            </label>
            <input
              type="number"
              min="60"
              max="1800"
              value={settings.analysis.timeout}
              onChange={(e) => updateSetting('analysis', 'timeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Max File Size (MB)
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={settings.analysis.maxFileSize}
              onChange={(e) => updateSetting('analysis', 'maxFileSize', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="mt-6 space-y-4">
          {[
            { 
              key: 'autoRefresh', 
              label: 'Auto-refresh analysis status', 
              description: 'Automatically update analysis progress' 
            },
            { 
              key: 'notifications', 
              label: 'Enable notifications', 
              description: 'Show toast notifications for completed analyses' 
            },
            { 
              key: 'enableDocker', 
              label: 'Enable Docker support', 
              description: 'Use Docker for reproducibility testing (requires Docker installation)' 
            }
          ].map(({ key, label, description }) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">{label}</label>
                <p className="text-xs text-muted-foreground">{description}</p>
              </div>
              <input
                type="checkbox"
                checked={settings.preferences[key as keyof typeof settings.preferences] as boolean || settings.analysis[key as keyof typeof settings.analysis] as boolean}
                onChange={(e) => {
                  const section = ['autoRefresh', 'notifications'].includes(key) ? 'preferences' : 'analysis'
                  updateSetting(section, key, e.target.checked)
                }}
                className="w-4 h-4 text-primary bg-background border-border rounded focus:ring-primary focus:ring-2"
              />
            </div>
          ))}
        </div>
      </motion.div>

      {/* About */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Info className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">About RePRO-Agent</h3>
        </div>
        
        <div className="space-y-2 text-sm text-muted-foreground">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>Built for:</strong> BioXAI Hackathon Scientific Outcomes Track</p>
          <p><strong>License:</strong> MIT License</p>
          <p><strong>Repository:</strong> <a href="https://github.com/yourusername/eliza-repro-hypothesis" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">GitHub</a></p>
        </div>
      </motion.div>
    </div>
  )
}

export default SettingsPage
