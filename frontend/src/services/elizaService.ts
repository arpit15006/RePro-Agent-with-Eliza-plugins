/**
 * Eliza Plugin Integration Service
 * Connects the frontend to all 4 Eliza plugins for unified scientific analysis
 */

export interface ElizaMessage {
  id: string;
  text: string;
  sender: 'user' | 'eliza';
  timestamp: Date;
  plugin?: string;
  action?: string;
}

export interface ElizaPlugin {
  name: string;
  port: number;
  description: string;
  actions: string[];
  status: 'running' | 'stopped' | 'error';
}

class ElizaService {
  private plugins: ElizaPlugin[] = [
    {
      name: 'manuscript-extractor',
      port: 3000,
      description: 'Analyzes scientific manuscripts and extracts metadata',
      actions: ['ANALYZE_MANUSCRIPT'],
      status: 'stopped'
    },
    {
      name: 'reproducibility-assistant',
      port: 3001,
      description: 'Assesses reproducibility of research and code',
      actions: ['ASSESS_REPRODUCIBILITY'],
      status: 'stopped'
    },
    {
      name: 'knowledge-graph-builder',
      port: 3002,
      description: 'Builds knowledge graphs from research data',
      actions: ['BUILD_KNOWLEDGE_GRAPH'],
      status: 'stopped'
    },
    {
      name: 'hypothesis-generator',
      port: 3003,
      description: 'Generates novel research hypotheses',
      actions: ['GENERATE_HYPOTHESES'],
      status: 'stopped'
    }
  ];

  private messages: ElizaMessage[] = [];
  private messageListeners: ((messages: ElizaMessage[]) => void)[] = [];

  constructor() {
    this.checkPluginStatus();
  }

  /**
   * Check the status of all Eliza plugins
   */
  async checkPluginStatus(): Promise<void> {
    for (const plugin of this.plugins) {
      try {
        const response = await fetch(`http://localhost:${plugin.port}/health`, {
          method: 'GET',
          timeout: 5000
        });
        plugin.status = response.ok ? 'running' : 'error';
      } catch (error) {
        plugin.status = 'stopped';
      }
    }
  }

  /**
   * Send a message to a specific Eliza plugin
   */
  async sendMessage(pluginName: string, message: string): Promise<ElizaMessage> {
    const plugin = this.plugins.find(p => p.name === pluginName);
    if (!plugin) {
      throw new Error(`Plugin ${pluginName} not found`);
    }

    // Add user message
    const userMessage: ElizaMessage = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
      plugin: pluginName
    };
    this.addMessage(userMessage);

    try {
      // Send to Eliza plugin via Socket.IO or REST API
      const response = await fetch(`http://localhost:${plugin.port}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          userId: 'frontend-user',
          agentId: plugin.name
        })
      });

      if (!response.ok) {
        throw new Error(`Plugin ${pluginName} returned error: ${response.status}`);
      }

      const data = await response.json();
      
      // Add Eliza response
      const elizaMessage: ElizaMessage = {
        id: (Date.now() + 1).toString(),
        text: data.response || data.text || 'No response from plugin',
        sender: 'eliza',
        timestamp: new Date(),
        plugin: pluginName,
        action: data.action
      };
      this.addMessage(elizaMessage);

      return elizaMessage;
    } catch (error) {
      console.error(`Error communicating with ${pluginName}:`, error);
      
      // Add error message
      const errorMessage: ElizaMessage = {
        id: (Date.now() + 1).toString(),
        text: `❌ Error communicating with ${plugin.description}. Please ensure the plugin is running.`,
        sender: 'eliza',
        timestamp: new Date(),
        plugin: pluginName
      };
      this.addMessage(errorMessage);

      return errorMessage;
    }
  }

  /**
   * Send message to the most appropriate plugin based on content
   */
  async sendSmartMessage(message: string): Promise<ElizaMessage> {
    const text = message.toLowerCase();
    
    // Determine which plugin to use based on keywords
    let targetPlugin = 'manuscript-extractor'; // default
    
    if (text.includes('reproducibility') || text.includes('reproduce') || text.includes('github') || text.includes('code')) {
      targetPlugin = 'reproducibility-assistant';
    } else if (text.includes('knowledge graph') || text.includes('graph') || text.includes('relationships') || text.includes('connections')) {
      targetPlugin = 'knowledge-graph-builder';
    } else if (text.includes('hypothesis') || text.includes('hypotheses') || text.includes('generate') || text.includes('predict')) {
      targetPlugin = 'hypothesis-generator';
    } else if (text.includes('manuscript') || text.includes('paper') || text.includes('analyze') || text.includes('extract')) {
      targetPlugin = 'manuscript-extractor';
    }

    return this.sendMessage(targetPlugin, message);
  }

  /**
   * Get all plugins
   */
  getPlugins(): ElizaPlugin[] {
    return [...this.plugins];
  }

  /**
   * Get all messages
   */
  getMessages(): ElizaMessage[] {
    return [...this.messages];
  }

  /**
   * Add a message to the conversation
   */
  private addMessage(message: ElizaMessage): void {
    this.messages.push(message);
    this.notifyListeners();
  }

  /**
   * Subscribe to message updates
   */
  onMessagesUpdate(callback: (messages: ElizaMessage[]) => void): () => void {
    this.messageListeners.push(callback);
    return () => {
      const index = this.messageListeners.indexOf(callback);
      if (index > -1) {
        this.messageListeners.splice(index, 1);
      }
    };
  }

  /**
   * Notify all listeners of message updates
   */
  private notifyListeners(): void {
    this.messageListeners.forEach(listener => listener(this.messages));
  }

  /**
   * Clear all messages
   */
  clearMessages(): void {
    this.messages = [];
    this.notifyListeners();
  }

  /**
   * Start a specific plugin (if not running)
   */
  async startPlugin(pluginName: string): Promise<boolean> {
    const plugin = this.plugins.find(p => p.name === pluginName);
    if (!plugin) return false;

    try {
      // This would typically involve starting the plugin process
      // For now, we'll just check if it's already running
      await this.checkPluginStatus();
      return plugin.status === 'running';
    } catch (error) {
      console.error(`Error starting plugin ${pluginName}:`, error);
      return false;
    }
  }

  /**
   * Get plugin status summary
   */
  getStatusSummary(): { running: number; total: number; plugins: ElizaPlugin[] } {
    const running = this.plugins.filter(p => p.status === 'running').length;
    return {
      running,
      total: this.plugins.length,
      plugins: this.plugins
    };
  }
}

// Export singleton instance
export const elizaService = new ElizaService();
export default elizaService;
