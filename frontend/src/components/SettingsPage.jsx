import { useState } from 'react';
import { api } from '../api';

export default function SettingsPage({ onClose, onConversationsDeleted }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDeleteClick = () => {
    setShowConfirm(true);
    setError(null);
  };

  const handleCancelDelete = () => {
    setShowConfirm(false);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      const response = await api.deleteAllConversations();
      setResult(response);
      setShowConfirm(false);
      onConversationsDeleted();
    } catch (err) {
      setError(err.message || 'Failed to delete conversations');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-bg-primary overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-8 py-6 border-b border-border-custom bg-gradient-to-r from-bg-secondary to-bg-primary">
        <div>
          <h1 className="font-display text-2xl font-semibold text-text-primary tracking-tight">
            Settings
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Manage your LLM Council preferences and data
          </p>
        </div>
        <button
          onClick={onClose}
          className="px-4 py-2 bg-bg-card border border-border-custom rounded-md text-sm font-medium text-text-secondary transition-base hover:bg-bg-secondary hover:border-accent-gold"
        >
          Back to Chat
        </button>
      </div>

      {/* Settings Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Data Management Section */}
          <section className="bg-bg-card rounded-lg border border-border-custom p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-accent-terracotta/10 flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-accent-terracotta"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </div>
              <div>
                <h2 className="font-display text-lg font-semibold text-text-primary">
                  Data Management
                </h2>
                <p className="text-sm text-text-muted">
                  Manage your stored conversations
                </p>
              </div>
            </div>

            <div className="border-t border-border-light pt-4">
              {!showConfirm ? (
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-text-primary mb-1">
                      Delete All Conversations
                    </h3>
                    <p className="text-sm text-text-muted">
                      Permanently remove all conversation history. This action cannot be undone.
                    </p>
                  </div>
                  <button
                    onClick={handleDeleteClick}
                    className="px-4 py-2 bg-accent-terracotta/10 border border-accent-terracotta/30 rounded-md text-sm font-medium text-accent-terracotta transition-base hover:bg-accent-terracotta hover:text-white hover:border-accent-terracotta"
                  >
                    Delete All
                  </button>
                </div>
              ) : (
                <div className="bg-accent-terracotta/5 border border-accent-terracotta/20 rounded-md p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-accent-terracotta/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg
                        className="w-4 h-4 text-accent-terracotta"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-text-primary mb-1">
                        Are you sure?
                      </h3>
                      <p className="text-sm text-text-muted mb-4">
                        This will permanently delete all your conversations. This action cannot be undone.
                      </p>
                      <div className="flex gap-3">
                        <button
                          onClick={handleConfirmDelete}
                          disabled={isDeleting}
                          className="px-4 py-2 bg-accent-terracotta border border-accent-terracotta rounded-md text-sm font-medium text-white transition-base hover:bg-accent-terracotta/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                          {isDeleting && (
                            <svg
                              className="animate-spin h-4 w-4"
                              fill="none"
                              viewBox="0 0 24 24"
                            >
                              <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                              />
                              <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                              />
                            </svg>
                          )}
                          {isDeleting ? 'Deleting...' : 'Yes, Delete All'}
                        </button>
                        <button
                          onClick={handleCancelDelete}
                          disabled={isDeleting}
                          className="px-4 py-2 bg-bg-secondary border border-border-custom rounded-md text-sm font-medium text-text-secondary transition-base hover:bg-bg-tertiary"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
                  {error}
                </div>
              )}

              {result && (
                <div className="mt-4 p-3 bg-accent-sage/10 border border-accent-sage/30 rounded-md text-sm text-accent-sage flex items-center gap-2">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  Successfully deleted {result.deleted_count} conversation
                  {result.deleted_count === 1 ? '' : 's'}
                </div>
              )}
            </div>
          </section>

          {/* About Section */}
          <section className="bg-bg-card rounded-lg border border-border-custom p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-accent-teal/10 flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-accent-teal"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="font-display text-lg font-semibold text-text-primary">
                  About
                </h2>
                <p className="text-sm text-text-muted">
                  LLM Council information
                </p>
              </div>
            </div>

            <div className="border-t border-border-light pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-text-secondary">Version</span>
                <span className="text-text-primary font-medium">1.0.0</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-text-secondary">Architecture</span>
                <span className="text-text-primary font-medium">
                  3-Stage Deliberation
                </span>
              </div>
              <div className="text-sm text-text-muted mt-4 leading-relaxed">
                LLM Council is a deliberative AI system where multiple language
                models collaboratively answer questions with anonymized peer
                review. The system uses a 3-stage process: individual responses,
                anonymized ranking, and synthesis by a chairman model.
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
