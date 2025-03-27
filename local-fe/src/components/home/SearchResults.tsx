import React from 'react';

interface SearchResult {
  doi: string;
  sentence: string;
  score: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
  error: string | null;
}

export function SearchResults({ results, isLoading, error }: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="w-full mt-8 p-4 rounded-md shadow">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600">Searching...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full mt-8 p-4 bg-red-50 rounded-md shadow">
        <h2 className="text-lg font-semibold text-red-600 mb-2">Search Error</h2>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="w-full mt-8">
      <h2 className="text-xl font-bold mb-4">Search Results</h2>
      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="border border-gray-200 rounded-md p-4 shadow hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <h3 className="text-lg font-semibold text-blue-600 mb-2 truncate">
                <a href={`https://doi.org/${result.doi}`} target="_blank" rel="noopener noreferrer" className="hover:underline">
                  {result.doi}
                </a>
              </h3>
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded ml-2">
                Similarity: {(result.score * 100).toFixed(1)}%
              </span>
            </div>
            <p className="text-gray-700 mt-2">{result.sentence}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 