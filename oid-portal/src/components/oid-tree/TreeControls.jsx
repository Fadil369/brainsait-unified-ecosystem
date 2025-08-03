/**
 * TreeControls Component
 * Search, filter, and control interface for the OID tree
 */

import React, { memo, useCallback, useMemo } from 'react';
import { useLanguage } from '../../hooks/useLanguage';
import { useOidTreeStore, HEALTHCARE_FILTERS } from '../../stores/oid-tree-store';

const SearchInput = memo(({ searchQuery, onSearchChange, isRTL, currentLanguage }) => {
  const [isFocused, setIsFocused] = React.useState(false);
  const [_searchSuggestions, _setSearchSuggestions] = React.useState([]);
  
  const handleSearchChange = useCallback((e) => {
    onSearchChange(e.target.value);
    // TODO: Add search suggestions logic
  }, [onSearchChange]);

  const handleClear = useCallback(() => {
    onSearchChange('');
  }, [onSearchChange]);

  return (
    <div className="healthcare-search-container">
      <input
        type="text"
        placeholder={currentLanguage === 'ar' ? 'البحث في الهيكل الطبي...' : 'Search medical hierarchy...'}
        className="healthcare-search-input"
        value={searchQuery}
        onChange={handleSearchChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        dir={isRTL ? 'rtl' : 'ltr'}
        aria-label={currentLanguage === 'ar' ? 'البحث في شجرة OID الطبية' : 'Search medical OID tree'}
      />
      
      {/* Search Icon */}
      <div className="healthcare-search-icon">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      {/* Clear Button */}
      {searchQuery && (
        <button
          className="healthcare-search-clear"
          onClick={handleClear}
          aria-label={currentLanguage === 'ar' ? 'مسح البحث' : 'Clear search'}
        >
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
      
      {/* Search Stats */}
      {searchQuery && (
        <div className={`text-xs text-clinical-text-tertiary mt-1 ${isRTL ? 'text-right' : 'text-left'}`}>
          {currentLanguage === 'ar' ? 'نتائج البحث لـ:' : 'Search results for:'} 
          <span className="font-medium text-clinical-text-secondary"> &quot;{searchQuery}&quot;</span>
        </div>
      )}
    </div>
  );
});

SearchInput.displayName = 'SearchInput';

const HealthcareFilter = memo(({ healthcareFilter, onFilterChange, currentLanguage }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  
  const handleFilterChange = useCallback((value) => {
    onFilterChange(value);
    setIsOpen(false);
  }, [onFilterChange]);

  const filterOptions = useMemo(() => 
    HEALTHCARE_FILTERS.map(filter => ({
      value: filter.value,
      label: filter.label[currentLanguage] || filter.label.en,
      icon: filter.icon,
      color: filter.color
    })), [currentLanguage]
  );

  const selectedFilter = filterOptions.find(f => f.value === healthcareFilter);

  return (
    <div className="healthcare-filter-container">
      <button
        className="healthcare-filter-select"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label={currentLanguage === 'ar' ? 'تصفية حسب فئة الرعاية الصحية' : 'Filter by healthcare category'}
      >
        <div className="flex items-center gap-2">
          {selectedFilter?.icon && (
            <span className={`text-sm ${selectedFilter.color}`}>
              {selectedFilter.icon}
            </span>
          )}
          <span className="truncate">{selectedFilter?.label || filterOptions[0].label}</span>
          <svg className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-clinical-bg-tertiary border border-clinical-border-primary rounded-md shadow-clinical-dropdown z-dropdown max-h-60 overflow-y-auto">
          {filterOptions.map(filter => (
            <button
              key={filter.value}
              className={`w-full px-3 py-2 text-left hover:bg-clinical-bg-interactive transition-colors flex items-center gap-2 ${
                filter.value === healthcareFilter ? 'bg-healthcare-primary-50 text-healthcare-primary' : 'text-clinical-text-primary'
              }`}
              onClick={() => handleFilterChange(filter.value)}
            >
              {filter.icon && (
                <span className={`text-sm ${filter.color}`}>
                  {filter.icon}
                </span>
              )}
              <span>{filter.label}</span>
              {filter.value === healthcareFilter && (
                <svg className="h-4 w-4 ml-auto text-healthcare-primary" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
});

HealthcareFilter.displayName = 'HealthcareFilter';

const TreeActions = memo(({ currentLanguage, onExpandAll, onCollapseAll, onRefresh, isLoading }) => {
  return (
    <div className="flex gap-2">
      <button
        onClick={onExpandAll}
        className="healthcare-btn healthcare-btn-sm healthcare-btn-primary"
        title={currentLanguage === 'ar' ? 'توسيع جميع العقد' : 'Expand all nodes'}
        aria-label={currentLanguage === 'ar' ? 'توسيع جميع العقد' : 'Expand all nodes'}
      >
        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <span>{currentLanguage === 'ar' ? 'توسيع' : 'Expand'}</span>
      </button>
      
      <button
        onClick={onCollapseAll}
        className="healthcare-btn healthcare-btn-sm healthcare-btn-outline"
        title={currentLanguage === 'ar' ? 'طي جميع العقد' : 'Collapse all nodes'}
        aria-label={currentLanguage === 'ar' ? 'طي جميع العقد' : 'Collapse all nodes'}
      >
        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
        </svg>
        <span>{currentLanguage === 'ar' ? 'طي' : 'Collapse'}</span>
      </button>
      
      <button
        onClick={onRefresh}
        className={`healthcare-btn healthcare-btn-sm healthcare-btn-ghost ${isLoading ? 'loading' : ''}`}
        title={currentLanguage === 'ar' ? 'تحديث البيانات' : 'Refresh data'}
        aria-label={currentLanguage === 'ar' ? 'تحديث البيانات' : 'Refresh data'}
        disabled={isLoading}
      >
        <svg className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{currentLanguage === 'ar' ? 'تحديث' : 'Refresh'}</span>
      </button>
    </div>
  );
});

TreeActions.displayName = 'TreeActions';

const PerformanceStats = memo(({ nodeCount, filteredCount, isLoading, currentLanguage, healthcareFilter }) => {
  if (isLoading) {
    return (
      <div className="tree-stats-display">
        <div className="healthcare-skeleton" style={{ width: '200px', height: '16px' }}></div>
      </div>
    );
  }

  const filterName = healthcareFilter !== 'all' ? healthcareFilter : null;
  
  return (
    <div className="tree-stats-display">
      <div className="stat-item">
        <svg className="h-4 w-4 text-healthcare-primary" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
        </svg>
        <span>{currentLanguage === 'ar' ? 'إجمالي العقد:' : 'Total nodes:'}</span>
        <span className="stat-value">{nodeCount.toLocaleString()}</span>
      </div>
      
      <div className="stat-item">
        <svg className="h-4 w-4 text-healthcare-success" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
        <span>{currentLanguage === 'ar' ? 'مرئية:' : 'Visible:'}</span>
        <span className="stat-value">{filteredCount.toLocaleString()}</span>
      </div>
      
      {filterName && (
        <div className="stat-item">
          <svg className="h-4 w-4 text-healthcare-info" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
          </svg>
          <span>{currentLanguage === 'ar' ? 'مرشح:' : 'Filter:'}</span>
          <span className="stat-value">{filterName}</span>
        </div>
      )}
      
      <div className="stat-item">
        <div className="performance-excellent"></div>
        <span className="text-xs">
          {currentLanguage === 'ar' ? 'محدث' : 'Updated'} {new Date().toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
});

PerformanceStats.displayName = 'PerformanceStats';

const TreeControls = memo(() => {
  const { currentLanguage, isRTL } = useLanguage();
  const {
    searchQuery,
    healthcareFilter,
    isLoading,
    flattenedNodes,
    setSearchQuery,
    setHealthcareFilter,
    expandAll,
    collapseAll,
    getVisibleNodes
  } = useOidTreeStore();

  const visibleNodes = useMemo(() => getVisibleNodes(), [getVisibleNodes]);
  const totalNodeCount = Object.keys(flattenedNodes).length;
  const filteredCount = visibleNodes.length;

  const handleSearchChange = useCallback((query) => {
    setSearchQuery(query);
  }, [setSearchQuery]);

  const handleFilterChange = useCallback((filter) => {
    setHealthcareFilter(filter);
  }, [setHealthcareFilter]);

  const handleRefresh = useCallback(() => {
    // TODO: Implement refresh logic
    window.location.reload();
  }, []);

  return (
    <div className={`healthcare-card ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header with Title */}
      <div className="healthcare-card-header">
        <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="healthcare-entity-indicator entity-service">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="healthcare-card-title">
              {currentLanguage === 'ar' ? 'شجرة الهوية الطبية الموحدة' : 'Unified Medical Identity Tree'}
            </h2>
          </div>
          
          {/* Real-time Status Indicator */}
          <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
            <div className="flex items-center gap-1">
              <div className="performance-excellent"></div>
              <span className="text-xs text-clinical-text-secondary">
                {currentLanguage === 'ar' ? 'متصل' : 'Live'}
              </span>
            </div>
          </div>
        </div>
        
        {/* Performance Stats */}
        <PerformanceStats 
          nodeCount={totalNodeCount} 
          filteredCount={filteredCount} 
          isLoading={isLoading}
          currentLanguage={currentLanguage}
          healthcareFilter={healthcareFilter}
        />
      </div>

      {/* Controls Body */}
      <div className="healthcare-card-body">
        <div className={`flex items-center gap-4 flex-wrap ${isRTL ? 'flex-row-reverse' : ''}`}>
          {/* Healthcare Category Filter */}
          <div className="relative">
            <HealthcareFilter
              healthcareFilter={healthcareFilter}
              onFilterChange={handleFilterChange}
              currentLanguage={currentLanguage}
            />
          </div>

          {/* Search Input */}
          <div className="flex-1 min-w-0">
            <SearchInput
              searchQuery={searchQuery}
              onSearchChange={handleSearchChange}
              isRTL={isRTL}
              currentLanguage={currentLanguage}
            />
          </div>

          {/* Tree Actions */}
          <TreeActions
            currentLanguage={currentLanguage}
            onExpandAll={expandAll}
            onCollapseAll={collapseAll}
            onRefresh={handleRefresh}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
});

TreeControls.displayName = 'TreeControls';

export default TreeControls;