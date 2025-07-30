import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import { 
  InterviewResult, 
  ProcessingState, 
  InterviewTranscriptRequest 
} from '@/lib/types';

interface UseInterviewProcessorReturn {
  result: InterviewResult | null;
  processingState: ProcessingState;
  processInterview: (transcript: string, model?: string) => Promise<void>;
  reset: () => void;
  isLoading: boolean;
  error: string | null;
}

export function useInterviewProcessor(): UseInterviewProcessorReturn {
  const [result, setResult] = useState<InterviewResult | null>(null);
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isLoading: false,
    progress: 0,
    currentTask: '',
    error: null,
  });

  const processInterview = useCallback(async (transcript: string, model?: string) => {
    // Reset previous state
    setResult(null);
    setProcessingState({
      isLoading: true,
      progress: 0,
      currentTask: 'Validating transcript...',
      error: null,
    });

    try {
      // Simulate progress updates
      const progressSteps = [
        { progress: 10, task: 'Validating transcript...' },
        { progress: 25, task: 'Preprocessing text...' },
        { progress: 40, task: 'Analyzing content with AI...' },
        { progress: 60, task: 'Extracting highlights and lowlights...' },
        { progress: 80, task: 'Identifying key information...' },
        { progress: 95, task: 'Finalizing results...' },
      ];

      // Update progress with delays to show realistic processing
      const progressInterval = setInterval(() => {
        setProcessingState(prev => {
          const nextStep = progressSteps.find(step => step.progress > prev.progress);
          if (nextStep) {
            return {
              ...prev,
              progress: nextStep.progress,
              currentTask: nextStep.task,
            };
          }
          return prev;
        });
      }, 1000);

      // Prepare request
      const request: InterviewTranscriptRequest = {
        transcript,
        model: model || 'anthropic/claude-3.5-sonnet',
      };

      // Make API call
      const response = await apiClient.processInterview(request);

      // Clear progress interval
      clearInterval(progressInterval);

      // Convert response to InterviewResult
      const interviewResult: InterviewResult = {
        summary: response.summary,
        highlights: response.highlights,
        lowlights: response.lowlights,
        key_named_entities: response.key_named_entities,
        processing_time: response.processing_time,
        model: response.model,
      };

      // Set final state
      setResult(interviewResult);
      setProcessingState({
        isLoading: false,
        progress: 100,
        currentTask: 'Complete',
        error: null,
      });

    } catch (error: unknown) {
      // Clear any running intervals
      const errorObj = error as Error & { message?: string };
      setProcessingState(() => {
        return {
          isLoading: false,
          progress: 0,
          currentTask: '',
          error: errorObj.message || 'An unexpected error occurred',
        };
      });

      console.error('Interview processing failed:', error);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setProcessingState({
      isLoading: false,
      progress: 0,
      currentTask: '',
      error: null,
    });
  }, []);

  return {
    result,
    processingState,
    processInterview,
    reset,
    isLoading: processingState.isLoading,
    error: processingState.error,
  };
}