import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
}) {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="w-[280px] bg-gradient-to-b from-bg-secondary to-bg-tertiary border-r border-border-custom flex flex-col h-screen relative overflow-hidden">
      {/* Stage progress indicator strip */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-stage1 via-stage2 to-stage3" />

      <div className="px-5 pt-7 pb-5 border-b border-border-custom flex-shrink-0">
        <h1 className="font-display text-2xl font-semibold text-text-primary tracking-tight mb-1">
          LLM Council
        </h1>
        <p className="text-xs text-text-muted tracking-wider uppercase mb-5">
          Deliberative AI System
        </p>
        <button
          onClick={onNewConversation}
          className="w-full py-3 px-4 bg-text-primary text-bg-card rounded-md text-sm font-medium transition-base hover:bg-accent-bronze hover:border-accent-bronze hover:-translate-y-px hover:shadow-md active:translate-y-0 active:shadow-sm flex items-center justify-center gap-2"
        >
          <span className="text-lg font-light leading-none">+</span>
          New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 min-h-0">
        {conversations.length === 0 ? (
          <div className="py-10 px-5 text-center text-text-muted text-sm leading-relaxed">
            <div className="text-3xl mb-3 opacity-50">💬</div>
            <div>No conversations yet</div>
            <div className="text-xs mt-2">Start a new one to begin</div>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`p-3.5 mb-1.5 rounded-md cursor-pointer transition-base border border-transparent ${
                conv.id === currentConversationId
                  ? 'bg-bg-card border-accent-gold shadow-md'
                  : 'bg-transparent hover:bg-bg-card hover:border-border-custom hover:shadow-sm'
              }`}
            >
              <div className={`text-sm mb-1 leading-snug truncate transition-fast ${
                conv.id === currentConversationId ? 'text-text-primary font-medium' : 'text-text-secondary'
              }`}>
                {conv.title || 'New Conversation'}
              </div>
              <div className="text-xs text-text-light flex items-center gap-1.5">
                <span className="inline-block w-1.5 h-1.5 bg-accent-sage rounded-full" />
                {conv.message_count || 0} messages · {formatDate(conv.created_at)}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t border-border-custom text-center flex-shrink-0">
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-bg-card border border-border-custom rounded-full text-xs text-text-muted tracking-wide">
          <span className="inline-block w-2 h-2 bg-gradient-to-br from-accent-gold to-accent-bronze rounded-full" />
          Multi-Stage Deliberation
        </div>
      </div>
    </div>
  );
}
