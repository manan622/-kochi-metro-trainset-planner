import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  Train,
  Settings
} from 'lucide-react';

const ManagementPortal = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  useEffect(() => {
    fetchFleetStatus();
  }, [selectedDate]);

  const fetchFleetStatus = async () => {
    try {
      setLoading(true);
      const data = await trainsetAPI.getFleetStatus(selectedDate);
      setFleetStatus(data);
    } catch (error) {
      setError('Failed to fetch fleet status');
      console.error('Error fetching fleet status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'fit':
        return 'text-green-600 bg-green-100';
      case 'unfit':
        return 'text-red-600 bg-red-100';
      case 'standby':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const StatCard = ({ title, value, icon: Icon, color = 'text-gray-600' }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 ${color}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <Layout title="Management Portal">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Management Portal - Strategic Overview">
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Fleet Management Overview</h2>
            <p className="text-gray-600">Strategic insights and operational planning</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 text-gray-400 mr-2" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-metro-primary focus:border-transparent"
              />
            </div>
            <button
              onClick={fetchFleetStatus}
              className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors flex items-center"
            >
              <Settings className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {fleetStatus && (
          <>
            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Trainsets"
                value={fleetStatus.summary.total_trainsets}
                icon={Train}
                color="text-blue-600"
              />
              <StatCard
                title="Fit for Service"
                value={fleetStatus.summary.fit}
                icon={CheckCircle}
                color="text-green-600"
              />
              <StatCard
                title="Unfit (Maintenance)"
                value={fleetStatus.summary.unfit}
                icon={AlertTriangle}
                color="text-red-600"
              />
              <StatCard
                title="On Standby"
                value={fleetStatus.summary.standby}
                icon={Clock}
                color="text-yellow-600"
              />
            </div>

            {/* Fleet Status Overview */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-metro-primary" />
                  Fleet Status Distribution
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Fit Trainsets */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-green-600 flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Fit for Service ({fleetStatus.summary.fit})
                    </h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {fleetStatus.trainsets
                        .filter(t => t.status === 'Fit')
                        .map(trainset => (
                          <div key={trainset.trainset_id} className="text-sm p-2 bg-green-50 rounded border">
                            <span className="font-medium">{trainset.trainset_id}</span>
                            <p className="text-xs text-green-700 mt-1">{trainset.reason}</p>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Unfit Trainsets */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-red-600 flex items-center">
                      <AlertTriangle className="h-4 w-4 mr-2" />
                      Unfit - Needs Attention ({fleetStatus.summary.unfit})
                    </h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {fleetStatus.trainsets
                        .filter(t => t.status === 'Unfit')
                        .map(trainset => (
                          <div key={trainset.trainset_id} className="text-sm p-2 bg-red-50 rounded border">
                            <span className="font-medium">{trainset.trainset_id}</span>
                            <p className="text-xs text-red-700 mt-1">{trainset.reason}</p>
                            {trainset.conflict_alerts.length > 0 && (
                              <div className="mt-1">
                                {trainset.conflict_alerts.map((alert, idx) => (
                                  <span key={idx} className="inline-block bg-red-200 text-red-800 text-xs px-2 py-1 rounded mr-1">
                                    {alert}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Standby Trainsets */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-yellow-600 flex items-center">
                      <Clock className="h-4 w-4 mr-2" />
                      On Standby ({fleetStatus.summary.standby})
                    </h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {fleetStatus.trainsets
                        .filter(t => t.status === 'Standby')
                        .map(trainset => (
                          <div key={trainset.trainset_id} className="text-sm p-2 bg-yellow-50 rounded border">
                            <span className="font-medium">{trainset.trainset_id}</span>
                            <p className="text-xs text-yellow-700 mt-1">{trainset.reason}</p>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Critical Alerts Summary */}
            {fleetStatus.summary.total_alerts > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-red-800 flex items-center mb-4">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Critical Alerts Requiring Management Attention
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {fleetStatus.trainsets
                    .filter(t => t.conflict_alerts.length > 0)
                    .map(trainset => (
                      <div key={trainset.trainset_id} className="bg-white rounded border border-red-200 p-4">
                        <h4 className="font-medium text-red-900">{trainset.trainset_id}</h4>
                        <div className="mt-2 space-y-1">
                          {trainset.conflict_alerts.map((alert, idx) => (
                            <div key={idx} className="text-sm text-red-700 flex items-center">
                              <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                              {alert}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Operational Insights */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2 text-metro-primary" />
                  Operational Insights
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Fleet Readiness</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Service Ready</span>
                        <span className="text-sm font-medium text-green-600">
                          {((fleetStatus.summary.fit / fleetStatus.summary.total_trainsets) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Needs Maintenance</span>
                        <span className="text-sm font-medium text-red-600">
                          {((fleetStatus.summary.unfit / fleetStatus.summary.total_trainsets) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Available Reserve</span>
                        <span className="text-sm font-medium text-yellow-600">
                          {((fleetStatus.summary.standby / fleetStatus.summary.total_trainsets) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
                    <div className="space-y-2 text-sm text-gray-600">
                      {fleetStatus.summary.unfit > 0 && (
                        <p>• Prioritize maintenance for {fleetStatus.summary.unfit} unfit trainsets</p>
                      )}
                      {fleetStatus.summary.total_alerts > 5 && (
                        <p>• High alert count ({fleetStatus.summary.total_alerts}) requires immediate attention</p>
                      )}
                      {fleetStatus.summary.fit / fleetStatus.summary.total_trainsets < 0.7 && (
                        <p>• Fleet readiness below 70% - consider operational adjustments</p>
                      )}
                      {fleetStatus.summary.standby > fleetStatus.summary.fit && (
                        <p>• Excess standby capacity available for service expansion</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default ManagementPortal;