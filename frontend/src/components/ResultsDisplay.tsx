'use client';

import { useState } from 'react';
import { ResultsDisplayProps } from '@/lib/types';
import { formatProcessingTime, copyToClipboard, cn } from '@/lib/utils';

export default function ResultsDisplay({ result, isLoading, error }: ResultsDisplayProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const handleCopy = async (text: string, section: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    }
  };

  const handleCopyAll = async () => {
    if (!result) return;
    
    const fullText = `Interview Summary
Generated with ${result.model}
${result.processing_time ? `Processing time: ${formatProcessingTime(result.processing_time)}` : ''}

SUMMARY
${result.summary}

HIGHLIGHTS
${result.highlights.map((item, index) => `${index + 1}. ${item}`).join('\n')}

LOWLIGHTS
${result.lowlights.map((item, index) => `${index + 1}. ${item}`).join('\n')}

KEY INFORMATION
${Object.entries(result.key_named_entities).map(([key, value]) => `${key}: ${value}`).join('\n')}`;

    await handleCopy(fullText, 'all');
  };

  if (isLoading) {
    return null; // Loading is handled by the LoadingSpinner component
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <svg className="w-6 h-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">
            Processing Failed
          </h3>
        </div>
        <p className="text-red-700 dark:text-red-300 mb-4">
          {error}
        </p>
        <div className="text-sm text-red-600 dark:text-red-400">
          <p>Please try again with a different transcript or check your connection.</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Interview Summary
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {result.model}
              </span>
              {result.processing_time && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {formatProcessingTime(result.processing_time)}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={handleCopyAll}
            className={cn(
              "flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors",
              "bg-blue-600 hover:bg-blue-700 text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            )}
          >
            {copiedSection === 'all' ? (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy All
              </>
            )}
          </button>
        </div>
      </div>

      <div className="p-6 space-y-8">
        {/* Summary Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Summary
            </h4>
            <button
              onClick={() => handleCopy(result.summary, 'summary')}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              {copiedSection === 'summary' ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-gray-900 dark:text-white leading-relaxed">
              {result.summary}
            </p>
          </div>
        </div>

        {/* Highlights Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Highlights
              <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                ({result.highlights.length})
              </span>
            </h4>
            <button
              onClick={() => handleCopy(result.highlights.join('\n'), 'highlights')}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              {copiedSection === 'highlights' ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="space-y-3">
            {result.highlights.length > 0 ? (
              result.highlights.map((highlight, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-green-600 dark:text-green-400">
                      {index + 1}
                    </span>
                  </div>
                  <p className="text-gray-900 dark:text-white leading-relaxed">
                    {highlight}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400 italic">
                No highlights identified in this interview.
              </p>
            )}
          </div>
        </div>

        {/* Lowlights Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Areas for Improvement
              <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                ({result.lowlights.length})
              </span>
            </h4>
            <button
              onClick={() => handleCopy(result.lowlights.join('\n'), 'lowlights')}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              {copiedSection === 'lowlights' ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="space-y-3">
            {result.lowlights.length > 0 ? (
              result.lowlights.map((lowlight, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-yellow-600 dark:text-yellow-400">
                      {index + 1}
                    </span>
                  </div>
                  <p className="text-gray-900 dark:text-white leading-relaxed">
                    {lowlight}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 dark:text-gray-400 italic">
                No areas for improvement identified in this interview.
              </p>
            )}
          </div>
        </div>

        {/* Key Information Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Key Information
              <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                ({Object.keys(result.key_named_entities).length})
              </span>
            </h4>
            <button
              onClick={() => handleCopy(
                Object.entries(result.key_named_entities)
                  .map(([key, value]) => `${key}: ${value}`)
                  .join('\n'),
                'entities'
              )}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              {copiedSection === 'entities' ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            {Object.keys(result.key_named_entities).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(result.key_named_entities).map(([key, value]) => (
                  <div key={key} className="flex flex-col space-y-1">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 capitalize">
                      {key.replace(/_/g, ' ')}
                    </dt>
                    <dd className="text-gray-900 dark:text-white">
                      {value || 'Not specified'}
                    </dd>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 italic">
                No key information extracted from this interview.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}