import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Stage2.css';

function deAnonymizeText(text, labelToModel) {
  if (!labelToModel) return text;

  let result = text;
  Object.entries(labelToModel).forEach(([label, model]) => {
    if (!model) return;
    const modelShortName = model.split('/')[1] || model;
    result = result.replace(new RegExp(label, 'g'), `**${modelShortName}**`);
  });
  return result;
}

function getModelShortName(model) {
  if (!model) return 'Unknown';
  return model.split('/')[1] || model;
}

export default function Stage2({ rankings, labelToModel, aggregateRankings }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!rankings || rankings.length === 0) {
    return null;
  }

  return (
    <div className="my-6 p-6 bg-bg-card rounded-2xl border border-border-custom shadow-sm border-l-4 border-l-stage2">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-8 h-8 rounded-md bg-stage2-light flex items-center justify-center text-base">⚖️</div>
        <h3 className="font-display text-lg font-semibold text-text-primary tracking-tight">
          Stage 2: Peer Rankings
        </h3>
      </div>

      {aggregateRankings && aggregateRankings.length > 0 && (
        <div className="mb-7">
          <div className="bg-gradient-to-br from-bg-secondary to-bg-tertiary p-5 rounded-xl border border-border-custom">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-lg">🏆</span>
              <h4 className="font-display text-base font-semibold text-text-primary">Aggregate Rankings</h4>
            </div>
            <p className="text-sm text-text-muted mb-4 ml-6 -mt-2">
              Combined results across all peer evaluations. Lower average rank is better.
            </p>
            <div className="flex flex-col gap-2">
              {aggregateRankings.map((agg, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 px-4 py-3 bg-bg-card rounded-lg border border-border-custom transition-fast hover:border-stage2 hover:shadow-sm"
                >
                  <span className={`flex items-center justify-center w-7 h-7 text-sm font-bold text-white rounded-full flex-shrink-0 ${
                    index < 3
                      ? 'bg-gradient-to-br from-accent-gold to-accent-bronze'
                      : 'bg-stage2'
                  }`}>
                    {index + 1}
                  </span>
                  <span className="flex-1 font-mono text-sm text-text-primary font-medium">
                    {getModelShortName(agg.model)}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1 px-2.5 py-1 bg-stage2-light rounded-full text-xs text-text-secondary font-medium">
                      Avg: <span className="text-stage2 font-semibold">{agg.average_rank.toFixed(2)}</span>
                    </span>
                    <span className="text-xs text-text-muted">
                      {agg.rankings_count} votes
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="mt-7">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-base">📋</span>
          <h4 className="font-display text-base font-semibold text-text-primary">Raw Evaluations</h4>
        </div>
        <p className="text-sm text-text-muted mb-4 ml-6">
          Each model evaluated all responses (anonymized as Response A, B, C, etc.) and provided rankings.
          Bold model names are shown for readability, but the original evaluation used anonymous labels.
        </p>

        <div className="flex gap-2 flex-wrap mb-4 p-1 bg-bg-secondary rounded-md">
          {rankings.map((rank, index) => (
            <button
              key={index}
              onClick={() => setActiveTab(index)}
              className={`px-4 py-2.5 rounded-md text-sm font-medium transition-base font-mono ${
                activeTab === index
                  ? 'bg-bg-card text-stage2 border border-stage2 shadow-sm'
                  : 'bg-transparent text-text-muted hover:bg-bg-card hover:text-text-secondary'
              }`}
            >
              {getModelShortName(rank.model)}
            </button>
          ))}
        </div>

        {rankings[activeTab] && (
        <div className="bg-bg-card p-5 rounded-xl border border-border-custom">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-light">
            <span className="inline-flex items-center px-2.5 py-1 bg-stage2-light border border-stage2 rounded-full font-mono text-xs text-stage2 font-medium">
              {getModelShortName(rankings[activeTab]?.model)}
            </span>
            {rankings[activeTab]?.model?.includes('/') && (
              <span className="font-mono text-xs text-text-light">
                {rankings[activeTab].model}
              </span>
            )}
          </div>
          <div className="markdown-content text-text-primary leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {deAnonymizeText(rankings[activeTab]?.ranking || '', labelToModel)}
            </ReactMarkdown>
          </div>

          {rankings[activeTab]?.parsed_ranking?.length > 0 && (
            <div className="mt-5 pt-5 border-t-2 border-border-light">
              <div className="flex items-center gap-1.5 mb-3">
                <span className="text-sm">✓</span>
                <span className="text-xs font-semibold text-stage2 uppercase tracking-wider">Extracted Ranking</span>
              </div>
              <ol className="m-0 pl-5 text-text-secondary">
                {rankings[activeTab].parsed_ranking.map((label, i) => (
                  <li
                    key={i}
                    className="my-1.5 font-mono text-sm py-1.5 px-2.5 bg-bg-secondary rounded-md border-l-2 border-l-stage2"
                  >
                    {labelToModel && labelToModel[label]
                      ? getModelShortName(labelToModel[label])
                      : label}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  );
}
