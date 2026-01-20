import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

const API_BASE = 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your healthcare assistant. How can I help you book an appointment today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          thread_id: threadId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      if (data.thread_id && !threadId) {
        setThreadId(data.thread_id);
      }

      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[500px] bg-card rounded-xl border shadow-lg overflow-hidden animate-fade-in">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b bg-primary/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">Healthcare Assistant</h3>
            <p className="text-sm text-muted-foreground">Online • Ready to help</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={cn(
              "flex items-start gap-3 animate-slide-up",
              message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            )}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
              message.role === 'user' 
                ? 'bg-primary' 
                : 'bg-muted'
            )}>
              {message.role === 'user' 
                ? <User className="w-4 h-4 text-primary-foreground" />
                : <Bot className="w-4 h-4 text-foreground" />
              }
            </div>
            <div className={cn(
              "max-w-[75%] px-4 py-3 rounded-2xl",
              message.role === 'user'
                ? 'bg-chat-user text-primary-foreground rounded-br-md'
                : 'bg-chat-assistant text-foreground rounded-bl-md'
            )}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
              <Bot className="w-4 h-4 text-foreground" />
            </div>
            <div className="bg-chat-assistant px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse-soft" style={{ animationDelay: '0s' }} />
                <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse-soft" style={{ animationDelay: '0.2s' }} />
                <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-pulse-soft" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-card">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1 px-4 py-3 bg-muted rounded-xl border-0 focus:outline-none focus:ring-2 focus:ring-primary/20 text-foreground placeholder:text-muted-foreground text-sm transition-all disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="w-12 h-12 bg-primary hover:bg-primary/90 disabled:bg-primary/50 rounded-xl flex items-center justify-center transition-all duration-200 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
          >
            <Send className="w-5 h-5 text-primary-foreground" />
          </button>
        </div>
      </div>
    </div>
  );
}
