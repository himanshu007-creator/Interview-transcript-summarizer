'use client';

import { useState, useCallback, useEffect } from 'react';
import { InterviewFormProps, ValidationError } from '@/lib/types';
import { validateTranscript, cn, debounce } from '@/lib/utils';

const MODELS = [
  { value: 'anthropic/claude-3.5-sonnet', label: 'Claude 3.5 Sonnet (Recommended)' },
  { value: 'openai/gpt-4o', label: 'GPT-4o' },
  { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini' },
];

export default function InterviewForm({ onSubmit, isLoading, error }: InterviewFormProps) {
  const [transcript, setTranscript] = useState('');
  const [selectedModel, setSelectedModel] = useState(MODELS[0].value);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);

  // Debounced validation function
  const debouncedValidate = useCallback(
    debounce((text: string) => {
      setIsValidating(true);
      const errors = validateTranscript(text);
      setValidationErrors(errors);
      setIsValidating(false);
    }, 300),
    []
  );

  // Validate transcript on change
  useEffect(() => {
    if (hasInteracted && transcript) {
      debouncedValidate(transcript);
    } else if (hasInteracted && !transcript) {
      setValidationErrors([{ field: 'transcript', message: 'Transcript is required' }]);
    }
  }, [transcript, hasInteracted, debouncedValidate]);

  const handleTranscriptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setTranscript(value);
    
    if (!hasInteracted) {
      setHasInteracted(true);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!hasInteracted) {
      setHasInteracted(true);
    }

    // Validate before submission
    const errors = validateTranscript(transcript);
    setValidationErrors(errors);

    if (errors.length === 0 && !isLoading) {
      try {
        await onSubmit(transcript, selectedModel);
      } catch (error) {
        // Error handling is managed by the parent component
        console.error('Form submission error:', error);
      }
    }
  };

  const handleClear = () => {
    setTranscript('');
    setValidationErrors([]);
    setHasInteracted(false);
  };

  const isFormValid = validationErrors.length === 0 && transcript.trim().length > 0;
  const showValidationErrors = hasInteracted && validationErrors.length > 0;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Interview Summary Generator
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Paste your interview transcript below to generate a comprehensive AI-powered summary with highlights, lowlights, and key candidate information.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Model Selection */}
          <div className="space-y-2">
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              AI Model
            </label>
            <select
              id="model"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={isLoading}
              className={cn(
                "w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600",
                "text-gray-900 dark:text-white",
                "disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed",
                "sm:text-sm"
              )}
            >
              {MODELS.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          {/* Transcript Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="transcript" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Interview Transcript
              </label>
              <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                {isValidating && (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-1 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Validating...
                  </span>
                )}
                <span>{transcript.length.toLocaleString()} / 50,000 characters</span>
              </div>
            </div>
            
            <div className="relative">
              <textarea
                id="transcript"
                value={transcript}
                onChange={handleTranscriptChange}
                disabled={isLoading}
                placeholder="Paste your interview transcript here. For best results, include timestamps in format HH:MM:SS.

Example:
00:00:10   introduction   Welcome to the interview, please introduce yourself
00:02:10   problem description   Can you describe a challenging problem you solved?
00:04:00   solution discussion   How did you approach this problem?"
                className={cn(
                  "w-full px-3 py-3 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:border-transparent resize-y",
                  "bg-white dark:bg-gray-800 text-gray-900 dark:text-white",
                  "placeholder-gray-500 dark:placeholder-gray-400",
                  "disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed",
                  "min-h-[200px] sm:min-h-[300px] md:min-h-[400px]",
                  showValidationErrors
                    ? "border-red-300 dark:border-red-600 focus:ring-red-500"
                    : "border-gray-300 dark:border-gray-600 focus:ring-blue-500",
                  "font-mono text-sm leading-relaxed"
                )}
                rows={12}
              />
              
              {/* Character count indicator */}
              <div className={cn(
                "absolute bottom-2 right-2 text-xs px-2 py-1 rounded",
                transcript.length > 45000
                  ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                  : transcript.length > 40000
                  ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                  : "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
              )}>
                {transcript.length > 50000 ? 'Too long' : 
                 transcript.length > 45000 ? 'Almost full' :
                 transcript.length < 50 ? 'Too short' : 'Good'}
              </div>
            </div>

            {/* Validation Errors */}
            {showValidationErrors && (
              <div className="space-y-1">
                {validationErrors.map((error, index) => (
                  <p key={index} className="text-sm text-red-600 dark:text-red-400 flex items-center">
                    <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {error.message}
                  </p>
                ))}
              </div>
            )}

            {/* Format Help */}
            {transcript.length > 0 && !transcript.includes(':') && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
                <div className="flex">
                  <svg className="w-5 h-5 text-blue-400 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      Tip: Include timestamps for better results
                    </h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      Format: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">HH:MM:SS category content</code>
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* API Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-red-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
                    Processing Error
                  </h4>
                  <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <button
              type="submit"
              disabled={!isFormValid || isLoading || isValidating}
              className={cn(
                "flex-1 flex items-center justify-center px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors",
                isFormValid && !isLoading && !isValidating
                  ? "bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500"
                  : "bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed",
                "sm:text-sm"
              )}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing Interview...
                </>
              ) : (
                'Generate Summary'
              )}
            </button>

            <button
              type="button"
              onClick={handleClear}
              disabled={isLoading || transcript.length === 0}
              className={cn(
                "px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors",
                "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700",
                "disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:text-gray-400 disabled:cursor-not-allowed",
                "sm:text-sm sm:flex-shrink-0"
              )}
            >
              Clear
            </button>
          </div>

          {/* Form Stats */}
          {transcript.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-md p-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {transcript.split('\n').filter(line => line.trim()).length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Lines</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {transcript.trim().split(/\s+/).length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Words</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {(transcript.match(/\d{2}:\d{2}:\d{2}/g) || []).length}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Timestamps</div>
                </div>
                <div>
                  <div className={cn(
                    "text-lg font-semibold",
                    isFormValid ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                  )}>
                    {isFormValid ? "✓" : "✗"}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Valid</div>
                </div>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}