import react from '@vitejs/plugin-react'
import autoprefixer from 'autoprefixer'
import tailwindcss from 'tailwindcss'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import eslint from 'vite-plugin-eslint'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'

// Healthcare-optimized Vite configuration with ultimate performance enhancements
export default defineConfig({
  plugins: [
    // ESLint integration for code quality
    eslint({
      cache: false,
      include: ['src/**/*.{js,jsx,ts,tsx}'],
      exclude: ['node_modules', 'dist']
    }),
    
    // Enhanced React configuration
    react({
      // Enable Fast Refresh for better development experience
      fastRefresh: true,
      // Configure Emotion for RTL support
      jsxImportSource: '@emotion/react',
      babel: {
        plugins: [
          ['@emotion/babel-plugin', {
            autoLabel: 'dev-only',
            sourceMap: process.env.NODE_ENV === 'development',
            cssPropOptimization: true
          }]
        ]
      }
    }),
    
    // Progressive Web App support for offline clinical scenarios
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'BrainSAIT Healthcare Unification Platform',
        short_name: 'BrainSAIT Health',
        description: 'Ultimate Unified Healthcare Intelligence Ecosystem for Saudi Arabia',
        theme_color: '#00D4FF',
        background_color: '#000000',
        display: 'standalone',
        orientation: 'portrait-primary',
        lang: 'ar-SA',
        dir: 'rtl',
        categories: ['health', 'medical', 'productivity'],
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        shortcuts: [
          {
            name: 'Patient Dashboard',
            short_name: 'Patients',
            description: 'Quick access to patient management',
            url: '/healthcare/patients',
            icons: [{ src: 'shortcut-patient.png', sizes: '96x96' }]
          },
          {
            name: 'NPHIES Claims',
            short_name: 'NPHIES',
            description: 'Access NPHIES claims dashboard',
            url: '/nphies',
            icons: [{ src: 'shortcut-nphies.png', sizes: '96x96' }]
          },
          {
            name: 'Emergency',
            short_name: 'Emergency',
            description: 'Emergency access interface',
            url: '/emergency',
            icons: [{ src: 'shortcut-emergency.png', sizes: '96x96' }]
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\..*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'healthcare-api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'healthcare-images',
              expiration: {
                maxEntries: 60,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
              }
            }
          },
          {
            urlPattern: /\.(?:woff|woff2|eot|ttf|otf)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'arabic-fonts',
              expiration: {
                maxEntries: 20,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              }
            }
          }
        ]
      }
    }),
    
    // Bundle analyzer for optimization insights
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true
    }),
    
    // Gzip and Brotli compression
    compression({
      algorithm: 'gzip',
      threshold: 1024
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024
    })
  ],
  
  server: {
    host: true,
    port: 5173,  // Changed to standard Vite port
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Direct API proxy without rewrite for compatibility
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/oid-tree': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/healthcare-identities': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/oids': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  
  build: {
    outDir: 'dist',
    minify: 'esbuild',
    sourcemap: process.env.NODE_ENV === 'development',
    target: 'es2020',
    assetsInlineLimit: 4096, // Inline small assets for faster loading
    
    // Advanced esbuild optimizations
    esbuild: {
      drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
      legalComments: 'none',
      minifyIdentifiers: true,
      minifySyntax: true,
      minifyWhitespace: true,
      treeShaking: true
    },
    
    // Healthcare-specific optimizations with advanced chunking
    rollupOptions: {
      external: [],
      treeshake: {
        preset: 'smallest',
        manualPureFunctions: ['console.log', 'console.info'],
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
        unknownGlobalSideEffects: false
      },
      output: {
        // Advanced chunk splitting for optimal caching and loading
        manualChunks: (id) => {
          // Core React chunks
          if (id.includes('react') || id.includes('react-dom')) {
            return 'vendor-react';
          }
          
          // Routing and navigation
          if (id.includes('react-router')) {
            return 'vendor-router';
          }
          
          // State management
          if (id.includes('zustand') || id.includes('immer') || id.includes('react-query')) {
            return 'state-management';
          }
          
          // Material-UI core
          if (id.includes('@mui/material') || id.includes('@mui/system')) {
            return 'ui-material';
          }
          
          // Material-UI icons (separate chunk for lazy loading)
          if (id.includes('@mui/icons-material')) {
            return 'ui-icons';
          }
          
          // Charts and data visualization
          if (id.includes('@mui/x-charts') || id.includes('@mui/x-data-grid') || id.includes('d3')) {
            return 'ui-charts';
          }
          
          // Emotion and styling
          if (id.includes('@emotion') || id.includes('stylis')) {
            return 'ui-styling';
          }
          
          // Internationalization
          if (id.includes('i18next') || id.includes('react-i18next')) {
            return 'i18n';
          }
          
          // Date utilities
          if (id.includes('date-fns')) {
            return 'utils-date';
          }
          
          // Virtualization for large datasets
          if (id.includes('react-window') || id.includes('react-virtualized')) {
            return 'virtualization';
          }
          
          // Healthcare-specific modules
          if (id.includes('fhir') || id.includes('hl7')) {
            return 'healthcare-fhir';
          }
          
          // Arabic language processing
          if (id.includes('arabic') || id.includes('bidi') || id.includes('reshaper')) {
            return 'arabic-processing';
          }
          
          // Crypto and security
          if (id.includes('crypto') || id.includes('bcrypt') || id.includes('jwt')) {
            return 'security';
          }
          
          // Other node_modules
          if (id.includes('node_modules')) {
            return 'vendor-others';
          }
          
          // Application code chunks by feature
          if (id.includes('/pages/')) {
            const pageName = id.split('/pages/')[1].split('/')[0].split('.')[0];
            return `page-${pageName.toLowerCase()}`;
          }
          
          if (id.includes('/components/')) {
            return 'components';
          }
          
          if (id.includes('/hooks/')) {
            return 'hooks';
          }
          
          if (id.includes('/contexts/')) {
            return 'contexts';
          }
          
          if (id.includes('/services/')) {
            return 'services';
          }
        },
        
        // Optimize asset names for caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
            ? chunkInfo.facadeModuleId.split('/').pop()
            : 'chunk';
          return `js/${facadeModuleId}-[hash].js`;
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          
          if (/\.(woff|woff2|eot|ttf|otf)$/.test(assetInfo.name)) {
            return `fonts/[name]-[hash].${ext}`;
          }
          
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/.test(assetInfo.name)) {
            return `images/[name]-[hash].${ext}`;
          }
          
          if (ext === 'css') {
            return `css/[name]-[hash].${ext}`;
          }
          
          return `assets/[name]-[hash].${ext}`;
        }
      }
    },
    
    // Optimize for healthcare performance requirements
    chunkSizeWarningLimit: 1000, // Increased for healthcare modules
    
    // Advanced build optimizations
    reportCompressedSize: false, // Disable for faster builds
    cssCodeSplit: true // Enable CSS code splitting
  },
  
  optimizeDeps: {
    // Force include critical dependencies for faster dev startup
    include: [
      'react',
      'react-dom',
      'react-dom/client',
      'react-router-dom',
      'zustand',
      'immer',
      '@emotion/react',
      '@emotion/styled',
      '@emotion/cache',
      'react-window',
      'react-query',
      '@mui/material',
      '@mui/system',
      'i18next',
      'react-i18next',
      'date-fns'
    ],
    exclude: [
      // Exclude large dependencies that don't need pre-bundling
      '@mui/x-data-grid',
      '@mui/x-charts',
      'workbox-window'
    ],
    // Force optimizations to speed up development
    force: process.env.NODE_ENV === 'development'
  },
  
  css: {
    postcss: {
      plugins: [
        tailwindcss,
        autoprefixer
      ]
    },
    // Enable CSS modules for component-specific styles
    modules: {
      localsConvention: 'camelCase',
      generateScopedName: '[name]__[local]___[hash:base64:5]'
    }
  },
  
  // Performance optimizations and environment variables
  define: {
    // Healthcare environment variables
    __HEALTHCARE_ENV__: JSON.stringify(process.env.NODE_ENV),
    __FHIR_ENABLED__: JSON.stringify(process.env.FHIR_ENABLED === 'true'),
    __RTL_SUPPORT__: JSON.stringify(true),
    __PWA_ENABLED__: JSON.stringify(true),
    __OFFLINE_SUPPORT__: JSON.stringify(true),
    __NEURAL_PROCESSING__: JSON.stringify(process.env.NEURAL_PROCESSING === 'true'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
  },
  
  // Worker support for background processing
  worker: {
    format: 'es',
    plugins: () => [react()]
  },
  
  // Preview configuration for production testing
  preview: {
    port: 5173,
    host: true,
    open: true
  },

  // Test configuration
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    css: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/setup.js',
      ]
    }
  }
})
