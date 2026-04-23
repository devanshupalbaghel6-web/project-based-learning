import React, { useEffect, useMemo, useState } from 'react';
import { ResourceCard, ResourceFilters } from './components';
import Spinner from '@components/Spinner';
import resourcesService from '@services/resources';

const ResourcesPage = () => {
  const [resources, setResources] = useState([]);
  const [savedResources, setSavedResources] = useState([]);
  const [recentQueries, setRecentQueries] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const normalizeResources = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.resources)) return payload.resources;
    return [];
  };

  const loadInitialData = async () => {
    setIsLoading(true);
    setError('');

    try {
      const [recommendedResult, savedResult, recentResult] = await Promise.allSettled([
        resourcesService.getRecommendedResources(),
        resourcesService.getSavedResources(),
        resourcesService.getRecentQueries(),
      ]);

      const recommendedResponse =
        recommendedResult.status === 'fulfilled' ? recommendedResult.value : { resources: [] };
      const savedResponse = savedResult.status === 'fulfilled' ? savedResult.value : [];
      const recentResponse = recentResult.status === 'fulfilled' ? recentResult.value : { queries: [] };

      setResources(normalizeResources(recommendedResponse));
      setSavedResources(Array.isArray(savedResponse) ? savedResponse : []);
      setRecentQueries(recentResponse?.queries || []);

      if (recommendedResult.status === 'rejected') {
        setError('No recommended resources yet. Use search to find curated material.');
      }
    } catch (initialError) {
      setError('Unable to load resources right now.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const displayedTitle = useMemo(() => {
    if (searchQuery.trim()) {
      return `Results for "${searchQuery.trim()}"`;
    }
    return 'Recommended for You';
  }, [searchQuery]);

  const refreshSavedAndQueries = async () => {
    try {
      const [savedResponse, recentResponse] = await Promise.all([
        resourcesService.getSavedResources(),
        resourcesService.getRecentQueries(),
      ]);
      setSavedResources(Array.isArray(savedResponse) ? savedResponse : []);
      setRecentQueries(recentResponse?.queries || []);
    } catch {
      // Best-effort refresh; keep existing data if this fails.
    }
  };

  const handleSearchSubmit = async (event, overrides = {}) => {
    event?.preventDefault();
    setError('');
    setIsLoading(true);

    const queryValue = overrides.query ?? searchQuery;
    const platformValue = overrides.platform ?? selectedPlatform;

    try {
      let response;
      if (!queryValue.trim() && platformValue !== 'all') {
        response = await resourcesService.getResourcesByPlatform(platformValue, 0, 20);
      } else {
        response = await resourcesService.searchResources(
          queryValue.trim() || 'programming tutorials',
          platformValue === 'all' ? null : [platformValue],
          20
        );
      }

      setResources(normalizeResources(response));
      await refreshSavedAndQueries();
    } catch (searchError) {
      setError('Resource search failed. Please try another query.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSave = async (resource) => {
    const resourceId = resource?._id || resource?.id;
    if (!resourceId) {
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      if (resource.saved) {
        await resourcesService.unsaveResource(resourceId);
      } else {
        await resourcesService.saveResource(resourceId);
      }

      setResources((prev) =>
        prev.map((item) =>
          (item._id || item.id) === resourceId ? { ...item, saved: !resource.saved } : item
        )
      );

      await refreshSavedAndQueries();
    } catch (saveError) {
      setError('Unable to update saved status for this resource.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading && resources.length === 0) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">Resources</h1>
        <p className="text-secondary-600">
          Curated learning materials from across the web
        </p>
        {error && <p className="text-sm text-error-DEFAULT mt-2">{error}</p>}
      </div>

      {/* Filters */}
      <ResourceFilters
        searchValue={searchQuery}
        onSearchValueChange={setSearchQuery}
        onSearchSubmit={handleSearchSubmit}
        selectedPlatform={selectedPlatform}
        onSelectPlatform={(platform) => {
          setSelectedPlatform(platform);
          handleSearchSubmit(null, { platform });
        }}
        isLoading={isLoading}
      />

      {/* Resources Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-heading font-semibold text-xl">
            {displayedTitle}
          </h2>
          <button
            className="text-primary-600 hover:text-primary-700 font-medium text-sm"
            onClick={loadInitialData}
          >
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {resources.map((resource) => (
            <ResourceCard
              key={resource._id || resource.id || resource.url}
              resource={resource}
              onToggleSave={handleToggleSave}
              isSaving={isSaving}
            />
          ))}
          {resources.length === 0 && (
            <p className="text-sm text-secondary-500">No resources found for the current filters.</p>
          )}
        </div>
      </div>

      {/* Recent Queries */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Recent Queries</h2>
        <div className="space-y-2">
          {recentQueries.map((item, index) => (
            <button
              key={`${item.query}-${index}`}
              className="w-full text-left flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors"
              onClick={() => {
                setSearchQuery(item.query);
                handleSearchSubmit(null, { query: item.query });
              }}
            >
              <span className="text-secondary-700">{item.query}</span>
              <span className="text-xs text-secondary-500">
                {item.last_used_at ? new Date(item.last_used_at).toLocaleDateString() : 'recent'}
              </span>
            </button>
          ))}
          {recentQueries.length === 0 && (
            <p className="text-sm text-secondary-500">No recent queries yet.</p>
          )}
        </div>
      </div>

      {/* Saved for Later */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Saved for Later</h2>
        <div className="space-y-2">
          {savedResources.map((item) => (
            <div key={item._id || item.id} className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg transition-colors">
              <a href={item.url} target="_blank" rel="noreferrer" className="text-secondary-700 hover:text-primary-600">
                {item.title}
              </a>
              <button
                type="button"
                className="text-xs text-primary-600"
                onClick={() => handleToggleSave({ ...item, saved: true })}
              >
                Remove
              </button>
            </div>
          ))}
          {savedResources.length === 0 && (
            <p className="text-sm text-secondary-500">No saved resources yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResourcesPage;
