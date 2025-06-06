import React, { useState, useEffect, useRef } from 'react';
import { elizaService, type ElizaMessage, type ElizaPlugin } from '../services/elizaService';

interface ElizaChatProps {
  className?: string;
}

export const ElizaChat: React.FC<ElizaChatProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<ElizaMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<string>('auto');
  const [plugins, setPlugins] = useState<ElizaPlugin[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Subscribe to message updates
    const unsubscribe = elizaService.onMessagesUpdate(setMessages);
    
    // Load initial data
    setMessages(elizaService.getMessages());
    setPlugins(elizaService.getPlugins());
    
    // Check plugin status
    elizaService.checkPluginStatus().then(() => {
      setPlugins(elizaService.getPlugins());
    });

    return unsubscribe;
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    try {
      if (selectedPlugin === 'auto') {
        await elizaService.sendSmartMessage(message);
      } else {
        await elizaService.sendMessage(selectedPlugin, message);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getPluginStatus = (pluginName: string) => {
    const plugin = plugins.find(p => p.name === pluginName);
    return plugin?.status || 'unknown';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500';
      case 'stopped': return 'text-red-500';
      case 'error': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return '🟢';
      case 'stopped': return '🔴';
      case 'error': return '🟡';
      default: return '⚪';
    }
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">🤖</span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">RePRO-Agent Chat</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Powered by {plugins.filter(p => p.status === 'running').length}/{plugins.length} Eliza Plugins
            </p>
          </div>
        </div>
        
        {/* Plugin Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-600 dark:text-gray-300">Plugin:</label>
          <select
            value={selectedPlugin}
            onChange={(e) => setSelectedPlugin(e.target.value)}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="auto">🎯 Auto-detect</option>
            {plugins.map(plugin => (
              <option key={plugin.name} value={plugin.name}>
                {getStatusIcon(plugin.status)} {plugin.name.replace('-', ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Plugin Status Bar */}
      <div className="px-4 py-2 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
        <div className="flex flex-wrap gap-2">
          {plugins.map(plugin => (
            <div key={plugin.name} className="flex items-center space-x-1 text-xs">
              <span className={getStatusColor(plugin.status)}>
                {getStatusIcon(plugin.status)}
              </span>
              <span className="text-gray-600 dark:text-gray-300">
                {plugin.name.replace('-', ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 py-8">
            <div className="text-4xl mb-4">🔬</div>
            <h3 className="text-lg font-medium mb-2">Welcome to RePRO-Agent Chat!</h3>
            <p className="text-sm">
              Ask me to analyze manuscripts, assess reproducibility, build knowledge graphs, or generate hypotheses.
            </p>
            <div className="mt-4 text-xs space-y-1">
              <p>💡 Try: "Analyze this paper: https://arxiv.org/abs/2301.00001"</p>
              <p>💡 Try: "Check reproducibility of https://github.com/user/repo"</p>
              <p>💡 Try: "Generate hypotheses about protein folding"</p>
            </div>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}
              >
                {message.sender === 'eliza' && message.plugin && (
                  <div className="text-xs opacity-75 mb-1">
                    📡 {message.plugin.replace('-', ' ')}
                  </div>
                )}
                <div className="whitespace-pre-wrap text-sm">{message.text}</div>
                <div className="text-xs opacity-75 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                <span className="text-sm text-gray-600 dark:text-gray-300">RePRO-Agent is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about manuscripts, reproducibility, knowledge graphs, or hypotheses..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-2 flex flex-wrap gap-2">
          <button
            onClick={() => setInputMessage('Analyze this manuscript: ')}
            className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            📄 Analyze Paper
          </button>
          <button
            onClick={() => setInputMessage('Check reproducibility of: ')}
            className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            🔬 Check Reproducibility
          </button>
          <button
            onClick={() => setInputMessage('Build knowledge graph for: ')}
            className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            🕸️ Build Graph
          </button>
          <button
            onClick={() => setInputMessage('Generate hypotheses about: ')}
            className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            💡 Generate Hypotheses
          </button>
        </div>
      </div>
    </div>
  );
};

export default ElizaChat;
