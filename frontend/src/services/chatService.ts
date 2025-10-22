const API_BASE_URL = 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  message: string;
  timestamp: string;
  isUser: boolean;
}

export interface Conversation {
  id?: string;
  conversation_id?: string;
  title?: string;
  subject?: string;
  messages: ChatMessage[];
  created_at: string;
}

class ChatService {
  async processChatMessage(userId: string, message: string): Promise<{ response: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/process-chat-message?user_id=${userId}&message=${encodeURIComponent(message)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error processing chat message:', error);
      throw error;
    }
  }

  async getAllConversations(userId: string): Promise<Conversation[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/get-all-conversations-by-user-id?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversations:', error);
      throw error;
    }
  }

  async getConversationById(userId: string, conversationId: string): Promise<Conversation> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/get-conversation-by-id?user_id=${userId}&conversation_id=${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }

  async createNewConversation(userId: string): Promise<{ conversation_id: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/new-conversation?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  }

  async switchToConversation(userId: string, conversationId: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/switch-to-conversation?user_id=${userId}&conversation_id=${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error switching conversation:', error);
      throw error;
    }
  }

  async deleteConversation(userId: string, conversationId: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/delete-conversation?user_id=${userId}&conversation_id=${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  async getActiveConversation(userId: string): Promise<Conversation | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/get-active-conversation?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // If no active conversation, return null (not an error)
        if (response.status === 404) {
          return null;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting active conversation:', error);
      return null;
    }
  }
}

export const chatService = new ChatService();
