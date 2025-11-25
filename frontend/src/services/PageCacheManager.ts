import { PageData } from "./PageFetcher";

/**
 * PageCacheManager
 *
 * Manages a cache of document pages for efficient navigation.
 * Implements Map-based storage with a maximum size limit.
 */

/**
 * Function type for fetching a page from the API
 */
export type PageFetchFunction = (
  documentId: string,
  pageNumber: number
) => Promise<PageData>;

export class PageCacheManager {
  private cache: Map<number, PageData> = new Map();
  private readonly maxSize: number = 5;
  private currentPage: number = 1;

  /**
   * Retrieve a page from the cache
   * @param pageNumber - The page number to retrieve
   * @returns The cached PageData or null if not found
   */
  getPage(pageNumber: number): PageData | null {
    return this.cache.get(pageNumber) || null;
  }

  /**
   * Store a page in the cache
   * @param pageNumber - The page number to store
   * @param page - The page data to cache
   */
  setPage(pageNumber: number, page: PageData): void {
    this.cache.set(pageNumber, page);
    this.evictIfNeeded();
  }

  /**
   * Set the current page for eviction distance calculations
   * @param pageNumber - The current page number
   */
  setCurrentPage(pageNumber: number): void {
    this.currentPage = pageNumber;
  }

  /**
   * Evict pages from cache if size exceeds maxSize limit.
   * Uses LRU-style eviction based on distance from current page.
   * Pages furthest from the current page are evicted first.
   * @private
   */
  private evictIfNeeded(): void {
    if (this.cache.size <= this.maxSize) {
      return;
    }

    // Remove pages until we're at or below maxSize
    while (this.cache.size > this.maxSize) {
      const firstPageNumber = Math.min(...this.cache.keys());
      this.cache.delete(firstPageNumber);
    }
  }

  /**
   * Clear all pages from the cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get the current cache size
   * @returns The number of pages currently cached
   */
  getCacheSize(): number {
    return this.cache.size;
  }

  /**
   * Check if a page exists in the cache
   * @param pageNumber - The page number to check
   * @returns True if the page is cached, false otherwise
   */
  hasPage(pageNumber: number): boolean {
    return this.cache.has(pageNumber);
  }

  /**
   * Preload pages within a radius of the current page
   * Fetches pages in parallel and stores them in the cache
   * @param documentId - The document ID to fetch pages from
   * @param currentPage - The current page number
   * @param totalPages - The total number of pages in the document
   * @param fetchPage - Function to fetch a page from the API
   * @param radius - The number of pages to preload before and after current page (default: 2)
   */
  async preloadPages(
    documentId: string,
    currentPage: number,
    totalPages: number,
    fetchPage: PageFetchFunction,
    radius: number = 2
  ): Promise<void> {
    const pagesToPreload: number[] = [];

    // Calculate pages within radius (±2 pages by default)
    for (let offset = -radius; offset <= radius; offset++) {
      const pageNumber = currentPage + offset;

      // Respect page boundaries (don't preload page 0 or beyond total_pages)
      // Only preload pages not already in cache
      if (
        pageNumber >= 1 &&
        pageNumber <= totalPages &&
        !this.hasPage(pageNumber)
      ) {
        pagesToPreload.push(pageNumber);
      }
    }

    // Fetch multiple pages in parallel using Promise.all
    if (pagesToPreload.length > 0) {
      const fetchPromises = pagesToPreload.map((pageNumber) =>
        fetchPage(documentId, pageNumber)
          .then((pageData) => {
            this.setPage(pageNumber, pageData);
          })
          .catch((error) => {
            console.error(`Failed to preload page ${pageNumber}:`, error);
            // Continue preloading other pages even if one fails
          })
      );

      await Promise.all(fetchPromises);
    }
  }
}
