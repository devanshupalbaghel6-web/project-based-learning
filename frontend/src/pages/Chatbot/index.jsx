import React, { useState } from 'react';
import Button from '@components/Button';
import resourcesService from '@services/resources';

const ChatbotPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const ask = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;
    setIsLoading(true);
    setError('');
    try {
      const payload = await resourcesService.searchResources(query.trim(), null, 8);
      setResults(payload?.resources || []);
    } catch {
      setError('Could not fetch context-aware resources right now.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">AI Assistant</h1>
        <p className="text-secondary-600">Ask a learning question and get context-aware resources instantly.</p>
      </div>

      <form onSubmit={ask} className="bg-white border border-secondary-200 rounded-xl p-4 flex flex-col sm:flex-row gap-3">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="How do I start with CCNA networking labs?"
          className="flex-1 px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Ask'}
        </Button>
      </form>

      {error && <p className="text-sm text-error-DEFAULT">{error}</p>}

      <div className="grid grid-cols-1 gap-3">
        {results.map((item) => (
          <a
            key={item._id || item.url}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="bg-white border border-secondary-200 rounded-lg p-4 hover:border-primary-400 transition-colors"
          >
            <p className="font-semibold">{item.title}</p>
            <p className="text-sm text-secondary-600 mt-1">{item.description}</p>
          </a>
        ))}
        {results.length === 0 && (
          <p className="text-sm text-secondary-500">No answers yet. Ask your first learning question.</p>
        )}
      </div>
    </div>
  );
};

export default ChatbotPage;

