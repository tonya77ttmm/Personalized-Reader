/**
 * TypeScript interfaces for page data and document metadata
 */

export interface PageData {
  page_number: number;
  content: string;
  start_word_index: number;
  end_word_index: number;
  word_count: number;
  context_before: string;
  context_after: string;
}

export interface DocumentMetadata {
  id: string;
  title: string;
  total_pages: number;
  total_words: number;
  words_per_page: number;
  uploaded_at: string;
}

/**
 * Configuration for retry logic
 */
interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
}

/**
 * PageFetcher class handles API calls to retrieve pages and document metadata
 * with built-in error handling and retry logic for network failures.
 */
export class PageFetcher {
  private readonly baseUrl: string;
  private readonly retryConfig: RetryConfig;

  constructor(
    baseUrl: string = "http://localhost:8000",
    retryConfig: Partial<RetryConfig> = {}
  ) {
    this.baseUrl = baseUrl;
    this.retryConfig = {
      maxRetries: retryConfig.maxRetries ?? 3,
      initialDelayMs: retryConfig.initialDelayMs ?? 1000,
      maxDelayMs: retryConfig.maxDelayMs ?? 5000,
    };
  }

  /**
   * Fetch document metadata including total pages and word counts
   * @param documentId - The unique identifier of the document
   * @returns Promise resolving to DocumentMetadata
   * @throws Error if the request fails after all retries
   */
  async fetchMetadata(documentId: string): Promise<DocumentMetadata> {
    const url = `${this.baseUrl}/api/documents/${documentId}/metadata`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch metadata: ${response.status}`);
    }

    const data: DocumentMetadata = await response.json();
    return data;
  }

  /**
   * Fetch a specific page from a document
   * @param documentId - The unique identifier of the document
   * @param pageNumber - The page number to fetch (1-indexed)
   * @returns Promise resolving to PageData
   * @throws Error if the request fails after all retries
   */
  async fetchPage(documentId: string, pageNumber: number): Promise<PageData> {
    const url = `${this.baseUrl}/api/documents/${documentId}/pages/${pageNumber}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch pagedata: ${response.status}`);
    }

    const data: PageData = await response.json();
    return data;
  }

  //   /**
  //    * Generic fetch method with exponential backoff retry logic
  //    * @param url - The URL to fetch
  //    * @param resourceName - Name of the resource for error messages
  //    * @returns Promise resolving to the parsed JSON response
  //    * @throws Error if all retry attempts fail
  //    */
  //   private async fetchWithRetry<T>(
  //     url: string,
  //     resourceName: string
  //   ): Promise<T> {
  //     let lastError: Error | null = null;

  //     for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
  //       try {
  //         const response = await fetch(url);

  //         if (!response.ok) {
  //           // Handle HTTP errors
  //           if (response.status === 404) {
  //             throw new Error(`${resourceName} not found (404)`);
  //           } else if (response.status >= 500) {
  //             throw new Error(`Server error (${response.status})`);
  //           } else {
  //             throw new Error(
  //               `HTTP error ${response.status}: ${response.statusText}`
  //             );
  //           }
  //         }

  //         const data = await response.json();
  //         return data as T;
  //       } catch (error) {
  //         lastError = error instanceof Error ? error : new Error(String(error));

  //         // Don't retry on 404 errors
  //         if (lastError.message.includes("404")) {
  //           throw lastError;
  //         }

  //         // If this was the last attempt, throw the error
  //         if (attempt === this.retryConfig.maxRetries) {
  //           throw new Error(
  //             `Failed to fetch ${resourceName} after ${
  //               this.retryConfig.maxRetries + 1
  //             } attempts: ${lastError.message}`
  //           );
  //         }

  //         // Calculate delay with exponential backoff
  //         const delay = Math.min(
  //           this.retryConfig.initialDelayMs * Math.pow(2, attempt),
  //           this.retryConfig.maxDelayMs
  //         );

  //         console.warn(
  //           `Attempt ${
  //             attempt + 1
  //           } failed for ${resourceName}, retrying in ${delay}ms...`,
  //           lastError.message
  //         );

  //         // Wait before retrying
  //         await this.sleep(delay);
  //       }
  //     }

  //     // This should never be reached, but TypeScript needs it
  //     throw lastError || new Error(`Failed to fetch ${resourceName}`);
  //   }

  //   /**
  //    * Sleep utility for retry delays
  //    * @param ms - Milliseconds to sleep
  //    */
  //   private sleep(ms: number): Promise<void> {
  //     return new Promise((resolve) => setTimeout(resolve, ms));
  //   }
}
