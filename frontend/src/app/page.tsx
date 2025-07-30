'use client';

import { useInterviewProcessor } from '@/hooks/useInterviewProcessor';
import InterviewForm from '@/components/InterviewForm';
import LoadingSpinner from '@/components/LoadingSpinner';
import ResultsDisplay from '@/components/ResultsDisplay';

export default function Home() {
  const { 
    processInterview, 
    isLoading, 
    error, 
    result, 
    reset, 
    processingState 
  } = useInterviewProcessor();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Interview Summary Generator
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Transform your interview transcripts into structured summaries with AI-powered analysis
          </p>
        </div>

        <div className="space-y-8">
          {/* Interview Form */}
          <InterviewForm
            onSubmit={processInterview}
            isLoading={isLoading}
            error={error}
          />

          {/* Loading State */}
          {isLoading && (
            <LoadingSpinner
              message={processingState.currentTask}
              progress={processingState.progress}
            />
          )}

          {/* Results Display */}
          {!isLoading && (result || error) && (
            <div className="space-y-6">
              <ResultsDisplay
                result={result}
                isLoading={isLoading}
                error={error}
              />
              
              {/* Action Buttons */}
              {(result || error) && (
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={reset}
                    className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  >
                    Process Another Interview
                  </button>
                  
                  {result && (
                    <button
                      onClick={() => {
                        const element = document.createElement('a');
                        const file = new Blob([JSON.stringify(result, null, 2)], {
                          type: 'application/json'
                        });
                        element.href = URL.createObjectURL(file);
                        element.download = `interview-summary-${new Date().toISOString().split('T')[0]}.json`;
                        document.body.appendChild(element);
                        element.click();
                        document.body.removeChild(element);
                      }}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      Download Results
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Help Section */}
          {!isLoading && !result && !error && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
                How to use the Interview Summary Generator
              </h3>
              <div className="grid md:grid-cols-2 gap-6 text-sm text-blue-800 dark:text-blue-200">
                <div>
                  <h4 className="font-medium mb-2">📝 Transcript Format</h4>
                  <ul className="space-y-1 text-blue-700 dark:text-blue-300">
                    <li>• Include timestamps for best results</li>
                    <li>• Format: HH:MM:SS category content</li>
                    <li>• Minimum 50 characters required</li>
                    <li>• Maximum 50,000 characters</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">🤖 AI Processing</h4>
                  <ul className="space-y-1 text-blue-700 dark:text-blue-300">
                    <li>• Generates comprehensive summary</li>
                    <li>• Extracts key highlights</li>
                    <li>• Identifies areas for improvement</li>
                    <li>• Captures candidate information</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
