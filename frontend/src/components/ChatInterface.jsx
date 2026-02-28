import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Stage1 from './Stage1';
import Stage2 from './Stage2';
import Stage3 from './Stage3';
import './ChatInterface.css';

export default function ChatInterface({
  conversation,
  onSendMessage,
  isLoading,
  webSearchEnabled,
  onToggleWebSearch,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!conversation) {
    return (
      <div className="flex-1 flex flex-col h-screen bg-bg-primary relative">
        <div className="flex-1 flex flex-col items-center justify-center h-full text-center p-12">
          <div className="text-6xl mb-6 opacity-80">🏛️</div>
          <h2 className="font-display text-3xl font-semibold text-text-primary tracking-tight mb-3">
            Welcome to LLM Council
          </h2>
          <p className="text-base text-text-muted mb-8 max-w-md leading-relaxed">
            A deliberative system where multiple AI models collaborate to answer your questions through anonymized peer review.
          </p>
          <div className="flex gap-4 flex-wrap justify-center">
            <div className="flex items-center gap-2 px-4 py-2.5 bg-bg-card border border-border-custom rounded-md text-sm text-text-secondary">
              <span className="text-base">📝</span>
              <span>Collect Responses</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2.5 bg-bg-card border border-border-custom rounded-md text-sm text-text-secondary">
              <span className="text-base">⚖️</span>
              <span>Peer Rankings</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2.5 bg-bg-card border border-border-custom rounded-md text-sm text-text-secondary">
              <span className="text-base">🎯</span>
              <span>Synthesized Answer</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const isEmpty = conversation.messages.length === 0;

  return (
    <div className="flex-1 flex flex-col h-screen bg-bg-primary relative">
      <div className="flex-1 overflow-y-auto p-8 scroll-smooth">
        {isEmpty ? (
          <div className="flex-1 flex flex-col items-center justify-center h-full text-center p-12">
            <div className="text-6xl mb-6 opacity-80">💭</div>
            <h2 className="font-display text-3xl font-semibold text-text-primary tracking-tight mb-3">
              Start a Conversation
            </h2>
            <p className="text-base text-text-muted max-w-md leading-relaxed">
              Ask a question to convene the council. Multiple models will deliberate and provide a refined answer.
            </p>
          </div>
        ) : (
          conversation.messages.map((msg, index) => (
            <div key={index} className="mb-10 animate-fade-in-up">
              {msg.role === 'user' ? (
                <div className="mb-6">
                  <div className="text-xs font-semibold text-text-muted mb-2.5 uppercase tracking-widest flex items-center gap-2">
                    <span className="inline-block w-1.5 h-1.5 bg-accent-teal rounded-full" />
                    You
                  </div>
                  <div className="bg-bg-card p-5 rounded-xl border border-border-custom text-text-primary leading-relaxed max-w-[85%] whitespace-pre-wrap shadow-sm">
                    <div className="markdown-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mb-6">
                  <div className="text-xs font-semibold text-text-muted mb-2.5 uppercase tracking-widest flex items-center gap-2">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-gradient-to-br from-accent-gold to-accent-bronze" />
                    Council Deliberation
                  </div>

                  {index === 0 && (
                    <div className="bg-gradient-to-r from-stage1-light to-bg-card p-5 rounded-xl border border-border-custom mb-6">
                      <div className="font-display text-lg font-semibold text-text-primary mb-2">
                        The Council Convenes
                      </div>
                      <div className="text-sm text-text-secondary">
                        The models are now deliberating on your question. This process happens in three stages:
                        individual responses, anonymized peer rankings, and final synthesis by the chairman.
                      </div>
                    </div>
                  )}

                  {msg.loading?.stage1 && (
                    <div className="flex items-center gap-3 px-5 py-4 bg-bg-card rounded-lg border border-border-custom shadow-sm mb-4 max-w-fit">
                      <div className="w-5 h-5 border-2 border-border-custom border-t-accent-gold rounded-full animate-spin-slow" />
                      <span className="text-sm text-text-secondary">Stage 1: Gathering individual perspectives...</span>
                    </div>
                  )}
                  {msg.stage1 && <Stage1 responses={msg.stage1} />}

                  {msg.loading?.stage2 && (
                    <div className="flex items-center gap-3 px-5 py-4 bg-bg-card rounded-lg border border-border-custom shadow-sm mb-4 max-w-fit">
                      <div className="w-5 h-5 border-2 border-border-custom border-t-accent-gold rounded-full animate-spin-slow" />
                      <span className="text-sm text-text-secondary">Stage 2: Conducting peer review...</span>
                    </div>
                  )}
                  {msg.stage2 && (
                    <Stage2
                      rankings={msg.stage2}
                      labelToModel={msg.metadata?.label_to_model}
                      aggregateRankings={msg.metadata?.aggregate_rankings}
                    />
                  )}

                  {msg.loading?.stage3 && (
                    <div className="flex items-center gap-3 px-5 py-4 bg-bg-card rounded-lg border border-border-custom shadow-sm mb-4 max-w-fit">
                      <div className="w-5 h-5 border-2 border-border-custom border-t-accent-gold rounded-full animate-spin-slow" />
                      <span className="text-sm text-text-secondary">Stage 3: Synthesizing final answer...</span>
                    </div>
                  )}
                  {msg.stage3 && <Stage3 finalResponse={msg.stage3} />}
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-center gap-3 px-6 py-5 bg-bg-card border border-border-custom rounded-xl max-w-fit shadow-sm">
            <div className="w-5 h-5 border-2 border-border-custom border-t-accent-gold rounded-full animate-spin-slow" />
            <span className="text-sm text-text-muted">The council is deliberating...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {isEmpty && (
        <form onSubmit={handleSubmit} className="flex flex-col gap-3 px-12 pb-8 pt-6 border-t border-border-custom bg-bg-card relative">
          <div className="absolute -top-px left-12 right-12 h-px bg-gradient-to-r from-transparent via-border-custom to-transparent" />
          <div className="flex items-end gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={3}
              placeholder="What would you like to ask the council? (Shift+Enter for new line)"
              className="flex-1 py-4 px-5 bg-bg-primary border border-border-custom rounded-xl text-text-primary text-[15px] leading-relaxed resize-y min-h-14 max-h-48 transition-base placeholder:text-text-light focus:border-accent-gold focus:ring-3 focus:ring-accent-gold/10 focus:bg-bg-card disabled:opacity-60 disabled:cursor-not-allowed disabled:bg-bg-secondary"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="py-4 px-7 bg-text-primary text-bg-card rounded-xl text-[15px] font-medium whitespace-nowrap h-14 flex items-center gap-2 transition-base hover:bg-accent-bronze hover:border-accent-bronze hover:-translate-y-px hover:shadow-md active:translate-y-0 active:shadow-sm disabled:opacity-40 disabled:cursor-not-allowed disabled:bg-text-light disabled:hover:translate-y-0 disabled:hover:shadow-none group"
            >
              Send
              <span className="text-lg transition-fast group-hover:translate-x-0.5">→</span>
            </button>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onToggleWebSearch}
              disabled={isLoading}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-base disabled:opacity-40 disabled:cursor-not-allowed ${
                webSearchEnabled
                  ? 'bg-accent-teal/10 text-accent-teal border border-accent-teal/30'
                  : 'bg-bg-primary text-text-muted border border-border-custom'
              }`}
              title={webSearchEnabled ? 'Web search is enabled - click to disable' : 'Web search is disabled - click to enable'}
            >
              <span className="text-base">{webSearchEnabled ? '🌐' : '🚫'}</span>
              <span>{webSearchEnabled ? 'Web Search On' : 'Web Search Off'}</span>
            </button>
            <span className="text-xs text-text-muted">
              {webSearchEnabled ? 'Models will use web search results' : 'Models will rely on their training data only'}
            </span>
          </div>
        </form>
      )}
    </div>
  );
}
