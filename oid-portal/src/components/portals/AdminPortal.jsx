import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useLanguage } from '../../hooks/useLanguage';

/**
 * Admin Portal Component
 * System administration and management interface
 */
const AdminPortal = () => {
  const { currentLanguage, isRTL } = useLanguage();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: currentLanguage === 'ar' ? 'لوحة التحكم' : 'Dashboard', icon: '📊' },
    { id: 'users', label: currentLanguage === 'ar' ? 'إدارة المستخدمين' : 'User Management', icon: '👥' },
    { id: 'system', label: currentLanguage === 'ar' ? 'إعدادات النظام' : 'System Settings', icon: '⚙️' },
    { id: 'audit', label: currentLanguage === 'ar' ? 'سجل الأحداث' : 'Audit Logs', icon: '📝' }
  ];

  return (
    <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <span className="text-2xl">⚙️</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">
                  {currentLanguage === 'ar' ? 'لوحة الإدارة' : 'Admin Portal'}
                </h1>
                <p className="text-gray-300">
                  {currentLanguage === 'ar' ? `مرحباً ${user?.name || ''}` : `Welcome ${user?.name || ''}`}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-gray-500 text-gray-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">156</div>
              <div className="text-gray-600 text-sm">
                {currentLanguage === 'ar' ? 'إجمالي المستخدمين' : 'Total Users'}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-green-600">89</div>
              <div className="text-gray-600 text-sm">
                {currentLanguage === 'ar' ? 'المستخدمون النشطون' : 'Active Users'}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-purple-600">1,234</div>
              <div className="text-gray-600 text-sm">
                {currentLanguage === 'ar' ? 'معرفات OID' : 'OID Identifiers'}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-orange-600">99.9%</div>
              <div className="text-gray-600 text-sm">
                {currentLanguage === 'ar' ? 'وقت التشغيل' : 'System Uptime'}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {currentLanguage === 'ar' ? 'إدارة المستخدمين' : 'User Management'}
            </h3>
            <p className="text-gray-600">
              {currentLanguage === 'ar' 
                ? 'إدارة المستخدمين والأدوار والصلاحيات' 
                : 'Manage users, roles, and permissions'}
            </p>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {currentLanguage === 'ar' ? 'إعدادات النظام' : 'System Settings'}
            </h3>
            <p className="text-gray-600">
              {currentLanguage === 'ar' 
                ? 'تكوين إعدادات النظام والأمان' 
                : 'Configure system settings and security'}
            </p>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {currentLanguage === 'ar' ? 'سجل الأحداث' : 'Audit Logs'}
            </h3>
            <p className="text-gray-600">
              {currentLanguage === 'ar' 
                ? 'مراجعة سجلات النظام والأنشطة' 
                : 'Review system logs and activities'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPortal;