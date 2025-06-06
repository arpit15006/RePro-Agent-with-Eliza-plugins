import type { Plugin } from '@elizaos/core';
import {
  type Action,
  type Content,
  type GenerateTextParams,
  type HandlerCallback,
  type IAgentRuntime,
  type Memory,
  ModelType,
  type Provider,
  type ProviderResult,
  Service,
  type State,
  logger,
} from '@elizaos/core';
import { z } from 'zod';
import axios from 'axios';
import FormData from 'form-data';

/**
 * Define the configuration schema for the manuscript extractor plugin
 *
 * @param {string} REPRO_AGENT_API_URL - The URL of the RePRO-Agent backend API
 * @param {string} OPENAI_API_KEY - OpenAI API key for AI-powered analysis
 * @returns {object} - The configured schema object
 */
const configSchema = z.object({
  REPRO_AGENT_API_URL: z
    .string()
    .url('Invalid API URL provided')
    .default('http://localhost:8000')
    .transform((val) => {
      logger.info(`Using RePRO-Agent API at: ${val}`);
      return val;
    }),
  OPENAI_API_KEY: z
    .string()
    .min(1, 'OpenAI API key is required for manuscript analysis')
    .optional()
    .transform((val) => {
      if (!val) {
        console.warn('Warning: OpenAI API key not provided - some features may be limited');
      }
      return val;
    }),
});

/**
 * Manuscript Analysis Action
 * Analyzes scientific manuscripts and generates hypotheses
 */
const analyzeManuscriptAction: Action = {
  name: 'ANALYZE_MANUSCRIPT',
  similes: ['ANALYZE_PAPER', 'EXTRACT_MANUSCRIPT', 'GENERATE_HYPOTHESES', 'ANALYZE_RESEARCH'],
  description: 'Analyzes scientific manuscripts and generates research hypotheses using AI',

  validate: async (runtime: IAgentRuntime, message: Memory, _state: State): Promise<boolean> => {
    // Check if message contains manuscript-related keywords
    const text = message.content.text?.toLowerCase() || '';
    const keywords = ['manuscript', 'paper', 'research', 'analyze', 'hypothesis', 'study', 'publication'];
    return keywords.some(keyword => text.includes(keyword));
  },

  handler: async (
    runtime: IAgentRuntime,
    message: Memory,
    _state: State,
    _options: any,
    callback: HandlerCallback,
    _responses: Memory[]
  ) => {
    try {
      logger.info('Handling ANALYZE_MANUSCRIPT action');

      const apiUrl = process.env.REPRO_AGENT_API_URL || 'http://localhost:8000';
      const messageText = message.content.text || '';

      // Extract paper URL or content from the message
      const urlMatch = messageText.match(/https?:\/\/[^\s]+/);
      const paperUrl = urlMatch ? urlMatch[0] : null;

      if (!paperUrl) {
        const responseContent: Content = {
          text: 'Please provide a URL to a scientific manuscript or paper that you\'d like me to analyze. I can extract key information and generate research hypotheses from it.',
          actions: ['ANALYZE_MANUSCRIPT'],
          source: message.content.source,
        };
        await callback(responseContent);
        return responseContent;
      }

      // Call the RePRO-Agent API
      try {
        const response = await axios.post(`${apiUrl}/analyze-paper`, {
          paper_url: paperUrl,
          focus_area: 'general research',
          num_hypotheses: 3
        });

        const jobId = response.data.job_id;

        // Poll for results
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds timeout

        while (attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second

          try {
            const statusResponse = await axios.get(`${apiUrl}/job-status/${jobId}`);

            if (statusResponse.data.status === 'completed') {
              const results = statusResponse.data.results;

              let responseText = `📄 **Manuscript Analysis Complete!**\n\n`;

              if (results.extracted_info) {
                responseText += `**Key Information:**\n`;
                responseText += `• Title: ${results.extracted_info.title || 'Not extracted'}\n`;
                responseText += `• Authors: ${results.extracted_info.authors || 'Not extracted'}\n`;
                responseText += `• Abstract: ${results.extracted_info.abstract?.substring(0, 200) || 'Not extracted'}...\n\n`;
              }

              if (results.hypotheses && results.hypotheses.length > 0) {
                responseText += `**Generated Research Hypotheses:**\n`;
                results.hypotheses.forEach((hypothesis: any, index: number) => {
                  responseText += `${index + 1}. ${hypothesis.hypothesis}\n`;
                  responseText += `   *Rationale:* ${hypothesis.rationale}\n\n`;
                });
              }

              if (results.reproducibility_score) {
                responseText += `**Reproducibility Score:** ${results.reproducibility_score}/10\n\n`;
              }

              responseText += `🔬 Analysis powered by RePRO-Agent - Making science more reproducible!`;

              const responseContent: Content = {
                text: responseText,
                actions: ['ANALYZE_MANUSCRIPT'],
                source: message.content.source,
              };

              await callback(responseContent);
              return responseContent;
            } else if (statusResponse.data.status === 'failed') {
              throw new Error(statusResponse.data.error || 'Analysis failed');
            }
          } catch (statusError) {
            logger.error('Error checking job status:', statusError);
          }

          attempts++;
        }

        throw new Error('Analysis timed out');

      } catch (apiError) {
        logger.error('Error calling RePRO-Agent API:', apiError);

        const responseContent: Content = {
          text: `❌ Sorry, I encountered an error while analyzing the manuscript. This could be due to:\n\n• The RePRO-Agent backend not being available\n• Network connectivity issues\n• Invalid manuscript URL\n\nPlease ensure the backend is running at ${apiUrl} and try again.`,
          actions: ['ANALYZE_MANUSCRIPT'],
          source: message.content.source,
        };

        await callback(responseContent);
        return responseContent;
      }

    } catch (error) {
      logger.error('Error in ANALYZE_MANUSCRIPT action:', error);

      const responseContent: Content = {
        text: '❌ An unexpected error occurred while analyzing the manuscript. Please try again later.',
        actions: ['ANALYZE_MANUSCRIPT'],
        source: message.content.source,
      };

      await callback(responseContent);
      return responseContent;
    }
  },

  examples: [
    [
      {
        name: '{{name1}}',
        content: {
          text: 'Can you analyze this research paper: https://arxiv.org/abs/2301.00001',
        },
      },
      {
        name: '{{name2}}',
        content: {
          text: '📄 **Manuscript Analysis Complete!**\n\n**Key Information:**\n• Title: Advanced Machine Learning Techniques\n• Authors: Smith et al.\n\n**Generated Research Hypotheses:**\n1. The proposed method could be extended to other domains...',
          actions: ['ANALYZE_MANUSCRIPT'],
        },
      },
    ],
  ],
};

/**
 * Manuscript Analysis Provider
 * Provides context about manuscript analysis capabilities
 */
const manuscriptAnalysisProvider: Provider = {
  name: 'MANUSCRIPT_ANALYSIS_PROVIDER',
  description: 'Provides context about scientific manuscript analysis and hypothesis generation capabilities',

  get: async (
    runtime: IAgentRuntime,
    message: Memory,
    _state: State
  ): Promise<ProviderResult> => {
    const messageText = message.content.text?.toLowerCase() || '';
    const isManuscriptRelated = ['manuscript', 'paper', 'research', 'analyze', 'hypothesis', 'study', 'publication']
      .some(keyword => messageText.includes(keyword));

    if (isManuscriptRelated) {
      return {
        text: `I can analyze scientific manuscripts and generate research hypotheses. I have access to the RePRO-Agent system which can:

• Extract key information from research papers
• Generate novel research hypotheses based on the content
• Assess reproducibility scores
• Build knowledge graphs from scientific literature
• Suggest follow-up research directions

Simply provide a URL to a scientific paper and I'll analyze it for you!`,
        values: {
          canAnalyzeManuscripts: true,
          hasReproAgent: true,
          apiUrl: process.env.REPRO_AGENT_API_URL || 'http://localhost:8000'
        },
        data: {
          capabilities: [
            'manuscript_extraction',
            'hypothesis_generation',
            'reproducibility_assessment',
            'knowledge_graph_building'
          ]
        },
      };
    }

    return {
      text: 'I can help with scientific manuscript analysis and research hypothesis generation.',
      values: {},
      data: {},
    };
  },
};

export class ManuscriptAnalysisService extends Service {
  static serviceType = 'manuscript-analysis';
  capabilityDescription =
    'Provides scientific manuscript analysis, hypothesis generation, and reproducibility assessment through the RePRO-Agent system.';

  private apiUrl: string;

  constructor(runtime: IAgentRuntime) {
    super(runtime);
    this.apiUrl = process.env.REPRO_AGENT_API_URL || 'http://localhost:8000';
  }

  static async start(runtime: IAgentRuntime) {
    logger.info('*** Starting Manuscript Analysis Service ***');
    const service = new ManuscriptAnalysisService(runtime);

    // Test API connectivity
    try {
      const response = await axios.get(`${service.apiUrl}/health`);
      logger.info('✅ RePRO-Agent API is accessible');
    } catch (error) {
      logger.warn('⚠️ RePRO-Agent API not accessible - some features may be limited');
    }

    return service;
  }

  static async stop(runtime: IAgentRuntime) {
    logger.info('*** Stopping Manuscript Analysis Service ***');
    const service = runtime.getService(ManuscriptAnalysisService.serviceType);
    if (!service) {
      throw new Error('Manuscript Analysis service not found');
    }
    service.stop();
  }

  async stop() {
    logger.info('*** Stopping Manuscript Analysis Service instance ***');
  }

  async analyzeManuscript(paperUrl: string, focusArea: string = 'general research', numHypotheses: number = 3) {
    try {
      const response = await axios.post(`${this.apiUrl}/analyze-paper`, {
        paper_url: paperUrl,
        focus_area: focusArea,
        num_hypotheses: numHypotheses
      });
      return response.data;
    } catch (error) {
      logger.error('Error analyzing manuscript:', error);
      throw error;
    }
  }

  async getJobStatus(jobId: string) {
    try {
      const response = await axios.get(`${this.apiUrl}/job-status/${jobId}`);
      return response.data;
    } catch (error) {
      logger.error('Error getting job status:', error);
      throw error;
    }
  }
}

const plugin: Plugin = {
  name: 'manuscript-extractor',
  description: 'Scientific manuscript analysis and hypothesis generation plugin for Eliza',
  // Set high priority for scientific analysis
  priority: 100,
  config: {
    REPRO_AGENT_API_URL: process.env.REPRO_AGENT_API_URL,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  },
  async init(config: Record<string, string>) {
    logger.info('*** Initializing Manuscript Extractor Plugin ***');
    try {
      const validatedConfig = await configSchema.parseAsync(config);

      // Set all environment variables at once
      for (const [key, value] of Object.entries(validatedConfig)) {
        if (value) process.env[key] = value;
      }

      logger.info('✅ Manuscript Extractor Plugin initialized successfully');
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(
          `Invalid plugin configuration: ${error.errors.map((e) => e.message).join(', ')}`
        );
      }
      throw error;
    }
  },
  models: {
    [ModelType.TEXT_SMALL]: async (
      _runtime,
      { prompt, stopSequences = [] }: GenerateTextParams
    ) => {
      return 'Never gonna give you up, never gonna let you down, never gonna run around and desert you...';
    },
    [ModelType.TEXT_LARGE]: async (
      _runtime,
      {
        prompt,
        stopSequences = [],
        maxTokens = 8192,
        temperature = 0.7,
        frequencyPenalty = 0.7,
        presencePenalty = 0.7,
      }: GenerateTextParams
    ) => {
      return 'Never gonna make you cry, never gonna say goodbye, never gonna tell a lie and hurt you...';
    },
  },
  routes: [
    {
      name: 'manuscript-analysis',
      path: '/analyze-manuscript',
      type: 'POST',
      handler: async (req: any, res: any) => {
        try {
          const { paperUrl, focusArea = 'general research', numHypotheses = 3 } = req.body;

          if (!paperUrl) {
            return res.status(400).json({
              error: 'Paper URL is required'
            });
          }

          const apiUrl = process.env.REPRO_AGENT_API_URL || 'http://localhost:8000';
          const response = await axios.post(`${apiUrl}/analyze-paper`, {
            paper_url: paperUrl,
            focus_area: focusArea,
            num_hypotheses: numHypotheses
          });

          res.json({
            message: 'Analysis started',
            jobId: response.data.job_id,
            status: 'processing'
          });
        } catch (error) {
          logger.error('Error in manuscript analysis route:', error);
          res.status(500).json({
            error: 'Failed to start manuscript analysis'
          });
        }
      },
    },
    {
      name: 'manuscript-status',
      path: '/manuscript-status/:jobId',
      type: 'GET',
      handler: async (req: any, res: any) => {
        try {
          const { jobId } = req.params;
          const apiUrl = process.env.REPRO_AGENT_API_URL || 'http://localhost:8000';

          const response = await axios.get(`${apiUrl}/job-status/${jobId}`);
          res.json(response.data);
        } catch (error) {
          logger.error('Error getting manuscript status:', error);
          res.status(500).json({
            error: 'Failed to get analysis status'
          });
        }
      },
    },
  ],
  events: {
    MESSAGE_RECEIVED: [
      async (params) => {
        logger.info('MESSAGE_RECEIVED event received');
        // print the keys
        logger.info(Object.keys(params));
      },
    ],
    VOICE_MESSAGE_RECEIVED: [
      async (params) => {
        logger.info('VOICE_MESSAGE_RECEIVED event received');
        // print the keys
        logger.info(Object.keys(params));
      },
    ],
    WORLD_CONNECTED: [
      async (params) => {
        logger.info('WORLD_CONNECTED event received');
        // print the keys
        logger.info(Object.keys(params));
      },
    ],
    WORLD_JOINED: [
      async (params) => {
        logger.info('WORLD_JOINED event received');
        // print the keys
        logger.info(Object.keys(params));
      },
    ],
  },
  services: [ManuscriptAnalysisService],
  actions: [analyzeManuscriptAction],
  providers: [manuscriptAnalysisProvider],
};

export default plugin;
