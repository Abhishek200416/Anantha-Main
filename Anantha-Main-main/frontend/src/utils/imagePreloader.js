// Image preloading utility for better performance

class ImagePreloader {
  constructor() {
    this.cache = new Map();
    this.loading = new Set();
  }

  // Preload a single image
  preloadImage(src) {
    return new Promise((resolve, reject) => {
      // Check if already cached
      if (this.cache.has(src)) {
        resolve(this.cache.get(src));
        return;
      }

      // Check if already loading
      if (this.loading.has(src)) {
        // Wait for the existing load to complete
        const checkInterval = setInterval(() => {
          if (this.cache.has(src)) {
            clearInterval(checkInterval);
            resolve(this.cache.get(src));
          }
        }, 50);
        return;
      }

      this.loading.add(src);

      const img = new Image();
      img.onload = () => {
        this.cache.set(src, img);
        this.loading.delete(src);
        resolve(img);
      };
      img.onerror = () => {
        this.loading.delete(src);
        reject(new Error(`Failed to load image: ${src}`));
      };
      img.src = src;
    });
  }

  // Preload multiple images
  async preloadImages(srcArray) {
    try {
      const promises = srcArray.map(src => this.preloadImage(src));
      return await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error preloading images:', error);
      return [];
    }
  }

  // Preload images with priority (load first N immediately, rest in batches)
  async preloadWithPriority(srcArray, priorityCount = 6) {
    const priority = srcArray.slice(0, priorityCount);
    const rest = srcArray.slice(priorityCount);

    // Load priority images immediately
    const priorityResults = await this.preloadImages(priority);
    
    // Load rest in background with small delay between batches
    if (rest.length > 0) {
      setTimeout(() => {
        this.preloadImagesInBatches(rest, 6, 100);
      }, 500);
    }

    return priorityResults;
  }

  // Preload images in batches with delay
  async preloadImagesInBatches(srcArray, batchSize = 5, delay = 100) {
    for (let i = 0; i < srcArray.length; i += batchSize) {
      const batch = srcArray.slice(i, i + batchSize);
      await this.preloadImages(batch);
      
      // Small delay between batches to avoid blocking
      if (i + batchSize < srcArray.length) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // Check if image is cached
  isCached(src) {
    return this.cache.has(src);
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
    this.loading.clear();
  }

  // Get cache size
  getCacheSize() {
    return this.cache.size;
  }
}

// Create singleton instance
const imagePreloader = new ImagePreloader();

export default imagePreloader;
