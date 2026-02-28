/**
 * API client for the LLM Council backend.
 */

// Use VITE_API_BASE if set, otherwise default to localhost for local dev
// In Docker, VITE_API_BASE should be set to empty string to use relative URLs with Vite proxy
const envBase = import.meta.env.VITE_API_BASE;
const API_BASE = envBase === undefined || envBase === null ? 'http://localhost:8001' : envBase.trim();

export const api = {
  /**
   * List all conversations.
   */
  async listConversations() {
    const response = await fetch(`${API_BASE}/api/conversations`);
    if (!response.ok) {
      throw new Error('Failed to list conversations');
    }
    return response.json();
  },

  /**
   * Create a new conversation.
   * @param {Object} settings - Optional conversation settings
   * @param {boolean} settings.web_search_enabled - Whether web search is enabled
   */
  async createConversation(settings = {}) {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    return response.json();
  },

  /**
   * Get a specific conversation.
   */
  async getConversation(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`
    );
    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }
    return response.json();
  },

  /**
   * Send a message in a conversation.
   */
  async sendMessage(conversationId, content) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    return response.json();
  },

  /**
   * Send a message and receive streaming updates.
   * @param {string} conversationId - The conversation ID
   * @param {string} content - The message content
   * @param {function} onEvent - Callback function for each event: (eventType, data) => void
   * @param {Object} options - Optional settings
   * @param {boolean} options.web_search_enabled - Whether to enable web search
   * @returns {Promise<void>}
   */
  async sendMessageStream(conversationId, content, onEvent, options = {}) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          web_search_enabled: options.web_search_enabled
        }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data);
            onEvent(event.type, event);
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  },

  /**
   * Update conversation settings.
   * @param {string} conversationId - The conversation ID
   * @param {Object} settings - Settings to update
   * @param {boolean} settings.web_search_enabled - Whether to enable web search
   */
  async updateConversationSettings(conversationId, settings) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/settings`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to update conversation settings');
    }
    return response.json();
  },

  /**
   * Delete all conversations.
   */
  async deleteAllConversations() {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete conversations');
    }
    return response.json();
  },
};
