import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage1.css';

export default function Stage1({ responses }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!responses || responses.length === 0) {
    return null;
  }

  const getModelShortName = (model) => {
    return model.split('/')[1] || model;
  };

  return (
    <div className="my-6 p-6 bg-bg-card rounded-2xl border border-border-custom shadow-sm border-l-4 border-l-stage1">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-8 h-8 rounded-md bg-stage1-light flex items-center justify-center text-base">📝</div>
        <h3 className="font-display text-lg font-semibold text-text-primary tracking-tight">
          Stage 1: Individual Responses
        </h3>
      </div>
      <p className="text-sm text-text-muted mb-5 ml-11 -mt-3">
        Each council member provides their independent response to your question.
      </p>

      <div className="flex gap-2 flex-wrap mb-4 p-1 bg-bg-secondary rounded-md">
        {responses.map((resp, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            className={`px-4 py-2.5 rounded-md text-sm font-medium transition-base font-mono ${
              activeTab === index
                ? 'bg-bg-card text-stage1 border border-stage1 shadow-sm'
                : 'bg-transparent text-text-muted hover:bg-bg-card hover:text-text-secondary'
            }`}
          >
            {getModelShortName(resp.model)}
          </button>
        ))}
      </div>

      <div className="bg-bg-primary p-5 rounded-xl border border-border-light">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-light">
          <span className="inline-flex items-center px-2.5 py-1 bg-stage1-light border border-stage1 rounded-full font-mono text-xs text-stage1 font-medium">
            {getModelShortName(responses[activeTab].model)}
          </span>
          {responses[activeTab].model.includes('/') && (
            <span className="font-mono text-xs text-text-light">
              {responses[activeTab].model}
            </span>
          )}
        </div>
        <div className="text-text-primary leading-relaxed">
          <ReactMarkdown>{responses[activeTab].response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
