import react from '@vitejs/plugin-react'
import autoprefixer from 'autoprefixer'
import tailwindcss from 'tailwindcss'
import { defineConfig } from 'vite'

// Healthcare-optimized Vite configuration
export default defineConfig({
  plugins: [
    react({
      // Enable Fast Refresh for better development experience
      fastRefresh: true,
      // Configure Emotion for RTL support
      jsxImportSource: '@emotion/react',
      babel: {
        plugins: [
          ['@emotion/babel-plugin', {
            autoLabel: 'dev-only',
            sourceMap: true,
            cssPropOptimization: true
          }]
        ]
      }
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
    
    // Healthcare-specific optimizations
    rollupOptions: {
      output: {
        // Optimize chunk splitting for healthcare modules
        manualChunks: {
          // Core dependencies
          'vendor-core': ['react', 'react-dom'],
          'vendor-router': ['react-router-dom'],
          
          // State management
          'state-management': ['zustand', 'immer'],
          
          // UI and styling
          'ui-core': ['@emotion/react', '@emotion/styled', '@emotion/cache'],
          'ui-components': ['@mui/material', '@mui/icons-material'],
          'ui-charts': ['@mui/x-charts', '@mui/x-data-grid'],
          
          // Healthcare-specific
          'healthcare-core': ['react-query'],
          'healthcare-utils': ['date-fns', 'date-fns-jalali'],
          
          // Virtualization for large datasets
          'virtualization': ['react-window', 'react-window-infinite-loader'],
          
          // Internationalization
          'i18n': ['i18next', 'react-i18next', 'i18next-browser-languagedetector'],
          
          // RTL support
          'rtl-support': ['stylis', 'stylis-plugin-rtl']
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
    
    // Enable compression
    reportCompressedSize: false, // Disable for faster builds
  },
  
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand',
      'immer',
      '@emotion/react',
      '@emotion/styled',
      'react-window',
      'react-query'
    ],
    exclude: [
      // Exclude large dependencies that don't need pre-bundling
      '@mui/x-data-grid',
      '@mui/x-charts'
    ]
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
  
  // Performance optimizations
  define: {
    // Healthcare environment variables
    __HEALTHCARE_ENV__: JSON.stringify(process.env.NODE_ENV),
    __FHIR_ENABLED__: JSON.stringify(process.env.FHIR_ENABLED === 'true'),
    __RTL_SUPPORT__: JSON.stringify(true)
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
