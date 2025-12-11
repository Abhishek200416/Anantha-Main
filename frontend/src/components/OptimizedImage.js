import React, { useState, useEffect } from 'react';
import imagePreloader from '../utils/imagePreloader';

const OptimizedImage = ({ 
  src, 
  alt, 
  className = '', 
  loading = 'lazy',
  priority = false,
  fallback = null,
  onLoad,
  onError,
  ...props 
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [imageSrc, setImageSrc] = useState(null);

  useEffect(() => {
    let isMounted = true;

    // Check if image is already cached
    if (imagePreloader.isCached(src)) {
      if (isMounted) {
        setImageSrc(src);
        setIsLoaded(true);
      }
      return;
    }

    // For priority images, preload immediately
    if (priority) {
      imagePreloader.preloadImage(src)
        .then(() => {
          if (isMounted) {
            setImageSrc(src);
            setIsLoaded(true);
            onLoad?.();
          }
        })
        .catch(() => {
          if (isMounted) {
            setHasError(true);
            onError?.();
          }
        });
    } else {
      // For non-priority images, just set src (browser handles lazy loading)
      setImageSrc(src);
    }

    return () => {
      isMounted = false;
    };
  }, [src, priority, onLoad, onError]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  if (hasError && fallback) {
    return fallback;
  }

  return (
    <div className="relative">
      {/* Placeholder while loading */}
      {!isLoaded && !hasError && (
        <div 
          className={`absolute inset-0 bg-gradient-to-br from-orange-50 to-red-50 animate-pulse ${className}`}
          style={{ minHeight: '200px' }}
        />
      )}
      
      {/* Actual image */}
      {imageSrc && !hasError && (
        <img
          src={imageSrc}
          alt={alt}
          className={`${className} ${!isLoaded ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
          loading={priority ? 'eager' : loading}
          onLoad={handleLoad}
          onError={handleError}
          {...props}
        />
      )}

      {/* Error fallback */}
      {hasError && !fallback && (
        <div 
          className={`bg-gray-200 flex items-center justify-center ${className}`}
          style={{ minHeight: '200px' }}
        >
          <div className="text-center text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm">Image unavailable</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizedImage;
