import React, { useState, useEffect } from 'react';
import { ElizaChat } from '../components/ElizaChat';
import { elizaService } from '../services/elizaService';
import { analysisStore } from '../stores/analysisStore';

export const ElizaIntegrationPage: React.FC = () => {
  const [pluginStatus, setPluginStatus] = useState(elizaService.getStatusSummary());
  const [isConnecting, setIsConnecting] = useState(false);

  useEffect(() => {
    // Check plugin status on mount
    checkAllPlugins();
    
    // Set up periodic status checks
    const interval = setInterval(checkAllPlugins, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const checkAllPlugins = async () => {
    await elizaService.checkPluginStatus();
    setPluginStatus(elizaService.getStatusSummary());
  };

  const handleConnectToBackend = async () => {
    setIsConnecting(true);
    try {
      // Test backend connection
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        // Send a test message to show integration
        await elizaService.sendSmartMessage(
          'Hello! I\'m connected to the RePRO-Agent backend. I can help you analyze manuscripts, assess reproducibility, build knowledge graphs, and generate hypotheses. What would you like to explore?'
        );
      } else {
        throw new Error('Backend not accessible');
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      await elizaService.sendSmartMessage(
        '❌ Could not connect to RePRO-Agent backend at http://localhost:8000. Please ensure the backend is running.'
      );
    } finally {
      setIsConnecting(false);
    }
  };

  const getOverallStatus = () => {
    if (pluginStatus.running === 0) return { status: 'offline', color: 'red', message: 'All plugins offline' };
    if (pluginStatus.running === pluginStatus.total) return { status: 'online', color: 'green', message: 'All plugins running' };
    return { status: 'partial', color: 'yellow', message: `${pluginStatus.running}/${pluginStatus.total} plugins running` };
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                🤖 Eliza Plugin Integration
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                Chat with your scientific research assistant powered by 4 specialized Eliza plugins
              </p>
            </div>
            
            {/* Status Indicator */}
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg bg-${overallStatus.color}-100 dark:bg-${overallStatus.color}-900`}>
                <div className={`w-3 h-3 rounded-full bg-${overallStatus.color}-500`}></div>
                <span className={`text-sm font-medium text-${overallStatus.color}-700 dark:text-${overallStatus.color}-300`}>
                  {overallStatus.message}
                </span>
              </div>
              
              <button
                onClick={checkAllPlugins}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Plugin Status Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                🔌 Plugin Status
              </h2>
              
              <div className="space-y-4">
                {pluginStatus.plugins.map(plugin => (
                  <div key={plugin.name} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {plugin.name.split('-').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                      </h3>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        plugin.status === 'running' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : plugin.status === 'error'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {plugin.status === 'running' ? '🟢 Running' : 
                         plugin.status === 'error' ? '🟡 Error' : '🔴 Stopped'}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                      {plugin.description}
                    </p>
                    
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Port: {plugin.port} | Actions: {plugin.actions.join(', ')}
                    </div>
                    
                    {plugin.status !== 'running' && (
                      <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                        ⚠️ Plugin not accessible. Ensure it's running on port {plugin.port}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Backend Connection */}
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="font-medium text-gray-900 dark:text-white mb-3">
                  🔗 Backend Integration
                </h3>
                
                <button
                  onClick={handleConnectToBackend}
                  disabled={isConnecting}
                  className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
                >
                  {isConnecting ? '🔄 Connecting...' : '🔗 Test Backend Connection'}
                </button>
                
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Backend: http://localhost:8000<br/>
                  Frontend: http://localhost:5173<br/>
                  Eliza Plugins: http://localhost:3000-3003
                </div>
              </div>

              {/* Quick Actions */}
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="font-medium text-gray-900 dark:text-white mb-3">
                  ⚡ Quick Actions
                </h3>
                
                <div className="space-y-2">
                  <button
                    onClick={() => elizaService.sendSmartMessage('Show me the status of all scientific analysis capabilities')}
                    className="w-full px-3 py-2 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                  >
                    📊 System Status
                  </button>
                  
                  <button
                    onClick={() => elizaService.sendSmartMessage('What can you help me with for scientific research?')}
                    className="w-full px-3 py-2 text-sm bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded hover:bg-purple-200 dark:hover:bg-purple-800"
                  >
                    ❓ Help & Capabilities
                  </button>
                  
                  <button
                    onClick={() => elizaService.clearMessages()}
                    className="w-full px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                  >
                    🗑️ Clear Chat
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <ElizaChat className="h-[800px]" />
          </div>
        </div>

        {/* Integration Info */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
            🔗 How Integration Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-blue-800 dark:text-blue-200">
            <div>
              <h3 className="font-medium mb-2">🎯 Smart Routing</h3>
              <p>Messages are automatically routed to the most appropriate Eliza plugin based on content analysis.</p>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">🔄 Real-time Communication</h3>
              <p>Direct integration with all 4 Eliza plugins running on separate ports for modular functionality.</p>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">🧠 Unified Intelligence</h3>
              <p>Combines manuscript analysis, reproducibility assessment, knowledge graphs, and hypothesis generation.</p>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">📊 Status Monitoring</h3>
              <p>Real-time monitoring of all plugin statuses with automatic health checks and error handling.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ElizaIntegrationPage;
