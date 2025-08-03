/**
 * RTL (Right-to-Left) Utilities
 * Comprehensive utilities for Arabic/RTL support in healthcare applications
 */

import { css } from '@emotion/react';

// RTL Direction Detection
export const isRTLLanguage = (language: string): boolean => {
  const rtlLanguages = ['ar', 'he', 'fa', 'ur', 'dv'];
  return rtlLanguages.includes(language.toLowerCase());
};

// Text Direction Utilities
export const getTextDirection = (language: string): 'ltr' | 'rtl' => {
  return isRTLLanguage(language) ? 'rtl' : 'ltr';
};

export const getOppositeDirection = (direction: 'ltr' | 'rtl'): 'ltr' | 'rtl' => {
  return direction === 'rtl' ? 'ltr' : 'rtl';
};

// CSS-in-JS RTL Support
export const rtlStyles = {
  // Flexbox utilities
  flexRow: (isRTL: boolean) => css`
    display: flex;
    flex-direction: ${isRTL ? 'row-reverse' : 'row'};
  `,
  
  flexRowReverse: (isRTL: boolean) => css`
    display: flex;
    flex-direction: ${isRTL ? 'row' : 'row-reverse'};
  `,
  
  // Spacing utilities
  marginLeft: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'margin-right' : 'margin-left'}: ${value};
  `,
  
  marginRight: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'margin-left' : 'margin-right'}: ${value};
  `,
  
  paddingLeft: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'padding-right' : 'padding-left'}: ${value};
  `,
  
  paddingRight: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'padding-left' : 'padding-right'}: ${value};
  `,
  
  // Positioning utilities
  left: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'right' : 'left'}: ${value};
  `,
  
  right: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'left' : 'right'}: ${value};
  `,
  
  // Text alignment
  textAlign: (isRTL: boolean) => css`
    text-align: ${isRTL ? 'right' : 'left'};
  `,
  
  textAlignOpposite: (isRTL: boolean) => css`
    text-align: ${isRTL ? 'left' : 'right'};
  `,
  
  // Border utilities
  borderLeft: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'border-right' : 'border-left'}: ${value};
  `,
  
  borderRight: (value: string, isRTL: boolean) => css`
    ${isRTL ? 'border-left' : 'border-right'}: ${value};
  `
};

// Tailwind CSS RTL Classes
export const getTailwindRTLClass = (baseClass: string, isRTL: boolean): string => {
  const rtlMappings: Record<string, string> = {
    'ml-': 'mr-',
    'mr-': 'ml-',
    'pl-': 'pr-',
    'pr-': 'pl-',
    'left-': 'right-',
    'right-': 'left-',
    'text-left': 'text-right',
    'text-right': 'text-left',
    'border-l-': 'border-r-',
    'border-r-': 'border-l-',
    'rounded-l-': 'rounded-r-',
    'rounded-r-': 'rounded-l-'
  };
  
  if (!isRTL) return baseClass;
  
  for (const [ltr, rtl] of Object.entries(rtlMappings)) {
    if (baseClass.includes(ltr)) {
      return baseClass.replace(ltr, rtl);
    }
  }
  
  return baseClass;
};

// Healthcare-specific RTL utilities
export const healthcareRTLUtils = {
  // Medical badge positioning
  getBadgePosition: (isRTL: boolean) => ({
    [isRTL ? 'left' : 'right']: '0.75rem'
  }),
  
  // Patient information layout
  getPatientInfoLayout: (isRTL: boolean) => css`
    display: flex;
    flex-direction: ${isRTL ? 'row-reverse' : 'row'};
    text-align: ${isRTL ? 'right' : 'left'};
    
    .patient-name {
      ${isRTL ? 'margin-left' : 'margin-right'}: 1rem;
    }
    
    .patient-id {
      ${isRTL ? 'margin-right' : 'margin-left'}: auto;
    }
  `,
  
  // Medical form layout
  getMedicalFormLayout: (isRTL: boolean) => css`
    .form-group {
      text-align: ${isRTL ? 'right' : 'left'};
    }
    
    .form-label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
    
    .form-input {
      width: 100%;
      text-align: ${isRTL ? 'right' : 'left'};
      direction: ${isRTL ? 'rtl' : 'ltr'};
    }
    
    .form-row {
      display: flex;
      flex-direction: ${isRTL ? 'row-reverse' : 'row'};
      gap: 1rem;
    }
  `,
  
  // Healthcare tree node layout
  getTreeNodeLayout: (isRTL: boolean, level: number) => css`
    display: flex;
    flex-direction: ${isRTL ? 'row-reverse' : 'row'};
    align-items: center;
    padding: 0.5rem;
    ${isRTL ? 'padding-right' : 'padding-left'}: ${level * 1.5 + 0.5}rem;
    
    .node-icon {
      ${isRTL ? 'margin-left' : 'margin-right'}: 0.5rem;
    }
    
    .node-content {
      flex: 1;
      text-align: ${isRTL ? 'right' : 'left'};
      direction: ${isRTL ? 'rtl' : 'ltr'};
    }
    
    .node-actions {
      ${isRTL ? 'margin-right' : 'margin-left'}: auto;
      display: flex;
      flex-direction: ${isRTL ? 'row-reverse' : 'row'};
      gap: 0.5rem;
    }
  `
};

// Font utilities for Arabic text
export const arabicFontUtils = {
  // Get appropriate font family for Arabic text
  getArabicFontFamily: () => [
    'Noto Sans Arabic',
    'Amiri',
    'Dubai',
    'Tahoma',
    'Arial Unicode MS',
    'sans-serif'
  ].join(', '),
  
  // Arabic typography styles
  getArabicTypography: () => css`
    font-family: ${arabicFontUtils.getArabicFontFamily()};
    font-feature-settings: 'liga' 1, 'calt' 1, 'kern' 1;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  `,
  
  // Mixed content (Arabic + English) handling
  getMixedContentStyles: () => css`
    .arabic-text {
      font-family: ${arabicFontUtils.getArabicFontFamily()};
      line-height: 1.6;
      letter-spacing: 0;
    }
    
    .english-text {
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.5;
    }
    
    .mixed-content {
      font-family: ${arabicFontUtils.getArabicFontFamily()}, system-ui, sans-serif;
      line-height: 1.6;
    }
  `
};

// Healthcare-specific text processing
export const healthcareTextUtils = {
  // Process medical terms for proper RTL display
  processMedicalTerm: (term: string, isArabic: boolean): string => {
    if (!isArabic) return term;
    
    // Handle mixed Arabic-English medical terms
    const englishPattern = /[a-zA-Z0-9.-]+/g;
    return term.replace(englishPattern, match => `\u202D${match}\u202C`);
  },
  
  // Format patient ID for RTL display
  formatPatientId: (id: string, isRTL: boolean): string => {
    // Always display IDs in LTR format
    return isRTL ? `\u202D${id}\u202C` : id;
  },
  
  // Format OID for RTL display
  formatOid: (oid: string, isRTL: boolean): string => {
    // OIDs should always be displayed in LTR format
    return isRTL ? `\u202D${oid}\u202C` : oid;
  }
};

// Responsive RTL utilities
export const responsiveRTLUtils = {
  // Mobile-first RTL breakpoints
  getResponsiveRTLStyles: (isRTL: boolean) => css`
    /* Mobile styles */
    .rtl-responsive {
      direction: ${isRTL ? 'rtl' : 'ltr'};
      text-align: ${isRTL ? 'right' : 'left'};
    }
    
    /* Tablet and up */
    @media (min-width: 768px) {
      .rtl-responsive-md {
        display: flex;
        flex-direction: ${isRTL ? 'row-reverse' : 'row'};
      }
    }
    
    /* Desktop and up */
    @media (min-width: 1024px) {
      .rtl-responsive-lg {
        grid-template-columns: ${isRTL ? '1fr 2fr' : '2fr 1fr'};
      }
    }
  `
};

// Export all utilities
export default {
  isRTLLanguage,
  getTextDirection,
  getOppositeDirection,
  rtlStyles,
  getTailwindRTLClass,
  healthcareRTLUtils,
  arabicFontUtils,
  healthcareTextUtils,
  responsiveRTLUtils
};