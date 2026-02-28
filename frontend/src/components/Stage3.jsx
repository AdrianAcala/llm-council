import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Stage3.css';

function getModelShortName(model) {
  return model.split('/')[1] || model;
}

export default function Stage3({ finalResponse }) {
  if (!finalResponse) {
    return null;
  }

  return (
    <div className="my-6 p-6 bg-bg-card rounded-2xl border border-border-custom shadow-sm border-l-4 border-l-stage3">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-8 h-8 rounded-md bg-stage3-light flex items-center justify-center text-base">🎯</div>
        <h3 className="font-display text-lg font-semibold text-text-primary tracking-tight">
          Stage 3: Final Council Answer
        </h3>
      </div>

      <div className="relative bg-gradient-to-br from-stage3-light to-bg-card p-7 rounded-xl border border-border-custom overflow-hidden">
        {/* Top accent line */}
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-stage3 to-accent-sage" />

        <div className="flex items-center justify-between mb-5 pb-4 border-b border-border-light">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-widest">Chairman</span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-stage3 rounded-full font-mono text-xs text-white font-medium">
              <span className="text-[10px]">👑</span>
              {getModelShortName(finalResponse.model)}
            </span>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-bg-card border border-stage3 rounded-full text-xs text-stage3 font-medium uppercase tracking-wide">
            <span>✨</span>
            Synthesized
          </span>
        </div>

        <div className="markdown-content text-text-primary leading-8 text-[15px]">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{finalResponse.response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
