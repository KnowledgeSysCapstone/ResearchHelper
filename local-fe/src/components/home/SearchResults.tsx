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
            <div className="flex flex-col">
              {/* DOI with similarity score */}
              <div className="flex justify-between items-center mb-3">
                <a 
                  href={`https://doi.org/${result.doi}`} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-blue-600 hover:underline font-medium"
                >
                  {result.doi}
                </a>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                  Similarity: {(result.score * 100).toFixed(1)}%
                </span>
              </div>
              
              {/* Sentence content */}
              <p className="text-gray-700">{result.sentence}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 