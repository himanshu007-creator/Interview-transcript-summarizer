'use client';

import { LoadingSpinnerProps } from '@/lib/types';
import { cn } from '@/lib/utils';

export default function LoadingSpinner({ 
  message = 'Processing...', 
  progress, 
  className 
}: LoadingSpinnerProps) {
  return (
    <div className={cn(
      "bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8",
      className
    )}>
      <div className="flex flex-col items-center justify-center space-y-6">
        {/* Animated Spinner */}
        <div className="relative">
          <div className="w-16 h-16 border-4 border-gray-200 dark:border-gray-700 rounded-full animate-spin border-t-blue-600"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 bg-blue-600 rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Progress Bar (if progress is provided) */}
        {typeof progress === 'number' && (
          <div className="w-full max-w-md">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Progress
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round(progress)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Status Message */}
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Processing Interview
          </h3>
          <p className="text-gray-600 dark:text-gray-400 max-w-md">
            {message}
          </p>
        </div>

        {/* Processing Steps Indicator */}
        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span>AI is analyzing your transcript</span>
        </div>

        {/* Estimated Time */}
        <div className="text-xs text-gray-400 dark:text-gray-500 text-center">
          <p>This usually takes 30-60 seconds</p>
          <p className="mt-1">Please don't close this page</p>
        </div>
      </div>
    </div>
  );
}