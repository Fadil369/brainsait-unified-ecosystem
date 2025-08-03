import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const SystemStatus = () => {
  const [systemMetrics, setSystemMetrics] = useState({
    overall: 'healthy',
    services: {
      api: { status: 'online', responseTime: 145, uptime: 99.9 },
      database: { status: 'online', responseTime: 23, uptime: 99.8 },
      nphies: { status: 'online', responseTime: 289, uptime: 98.5 },
      ai_service: { status: 'online', responseTime: 567, uptime: 99.2 },
      cache: { status: 'online', responseTime: 12, uptime: 99.9 },
      queue: { status: 'warning', responseTime: 1200, uptime: 97.8 }
    },
    performance: {
      cpu: 45,
      memory: 67,
      disk: 34,
      network: 23
    },
    activeUsers: 127,
    activeConnections: 89,
    requestsPerSecond: 234,
    errorRate: 0.02
  });

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        performance: {
          cpu: Math.max(20, Math.min(90, prev.performance.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(30, Math.min(85, prev.performance.memory + (Math.random() - 0.5) * 8)),
          disk: Math.max(20, Math.min(70, prev.performance.disk + (Math.random() - 0.5) * 5)),
          network: Math.max(10, Math.min(60, prev.performance.network + (Math.random() - 0.5) * 15))
        },
        activeUsers: Math.max(50, Math.min(200, prev.activeUsers + Math.floor((Math.random() - 0.5) * 10))),
        activeConnections: Math.max(30, Math.min(150, prev.activeConnections + Math.floor((Math.random() - 0.5) * 8))),
        requestsPerSecond: Math.max(100, Math.min(500, prev.requestsPerSecond + Math.floor((Math.random() - 0.5) * 50)))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const _getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPerformanceColor = (value) => {
    if (value < 50) return 'bg-green-500';
    if (value < 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
        <div className="flex items-center space-x-2">
          <div className="flex items-center">
            <div className={`h-2 w-2 rounded-full ${
              systemMetrics.overall === 'healthy' ? 'bg-green-500' : 
              systemMetrics.overall === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            }`}></div>
            <span className="ml-2 text-sm text-gray-600 capitalize">
              {systemMetrics.overall}
            </span>
          </div>
          <span className="text-xs text-gray-400">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Service Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {Object.entries(systemMetrics.services).map(([service, data]) => (
          <motion.div
            key={service}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-50 rounded-lg p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-900 capitalize">
                {service.replace('_', ' ')}
              </h3>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(data.status)}`}>
                {data.status}
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-600">
                <span>Response Time:</span>
                <span>{data.responseTime}ms</span>
              </div>
              <div className="flex justify-between text-xs text-gray-600">
                <span>Uptime:</span>
                <span>{data.uptime}%</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Performance Metrics */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(systemMetrics.performance).map(([metric, value]) => (
            <div key={metric} className="text-center">
              <div className="relative w-16 h-16 mx-auto mb-2">
                <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-gray-200"
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <path
                    className={getPerformanceColor(value).replace('bg-', 'text-')}
                    strokeDasharray={`${value}, 100`}
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-sm font-semibold text-gray-900">{value}%</span>
                </div>
              </div>
              <p className="text-xs text-gray-600 capitalize">{metric}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Real-time Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {systemMetrics.activeUsers}
          </div>
          <div className="text-sm text-blue-800">Active Users</div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {systemMetrics.activeConnections}
          </div>
          <div className="text-sm text-green-800">Active Connections</div>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {systemMetrics.requestsPerSecond}
          </div>
          <div className="text-sm text-purple-800">Requests/sec</div>
        </div>
        
        <div className="bg-orange-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {systemMetrics.errorRate}%
          </div>
          <div className="text-sm text-orange-800">Error Rate</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 flex justify-end space-x-3">
        <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          View Logs
        </button>
        <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">
          Run Diagnostics
        </button>
      </div>
    </div>
  );
};

export default SystemStatus;
