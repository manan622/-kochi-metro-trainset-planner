import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  Filter,
  FileText,
  Wrench,
  Eye
} from 'lucide-react';

const InspectionPortal = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

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

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'fit':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'unfit':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'standby':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'fit':
        return 'bg-green-100 border-green-200 text-green-800';
      case 'unfit':
        return 'bg-red-100 border-red-200 text-red-800';
      case 'standby':
        return 'bg-yellow-100 border-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-100 border-gray-200 text-gray-800';
    }
  };

  const filteredTrainsets = fleetStatus?.trainsets?.filter(trainset => {
    const matchesStatus = filterStatus === 'all' || trainset.status.toLowerCase() === filterStatus;
    const matchesSearch = trainset.trainset_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  }) || [];

  const getPriorityTrainsets = () => {
    if (!fleetStatus) return [];
    return fleetStatus.trainsets
      .filter(t => t.status === 'Unfit' || t.conflict_alerts.length > 0)
      .sort((a, b) => b.conflict_alerts.length - a.conflict_alerts.length);
  };

  if (loading) {
    return (
      <Layout title="Inspection Portal">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Inspection Portal - Technical Assessment">
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Trainset Inspection Overview</h2>
            <p className="text-gray-600">Technical assessment and maintenance planning</p>
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
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {fleetStatus && (
          <>
            {/* Priority Alerts */}
            {getPriorityTrainsets().length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-red-800 flex items-center mb-4">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Priority Inspection Required ({getPriorityTrainsets().length} trainsets)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {getPriorityTrainsets().slice(0, 6).map(trainset => (
                    <div key={trainset.trainset_id} className="bg-white rounded border border-red-200 p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-red-900">{trainset.trainset_id}</h4>
                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                          {trainset.conflict_alerts.length} alerts
                        </span>
                      </div>
                      <p className="text-sm text-red-700 mb-2">{trainset.reason}</p>
                      <div className="space-y-1">
                        {trainset.conflict_alerts.slice(0, 2).map((alert, idx) => (
                          <div key={idx} className="text-xs text-red-600 flex items-center">
                            <div className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></div>
                            {alert}
                          </div>
                        ))}
                        {trainset.conflict_alerts.length > 2 && (
                          <div className="text-xs text-red-500">
                            +{trainset.conflict_alerts.length - 2} more issues
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Filters and Search */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Search trainsets..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-metro-primary focus:border-transparent"
                    />
                  </div>
                  
                  <div className="relative">
                    <Filter className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="pl-10 pr-8 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-metro-primary focus:border-transparent appearance-none bg-white"
                    >
                      <option value="all">All Status</option>
                      <option value="fit">Fit</option>
                      <option value="unfit">Unfit</option>
                      <option value="standby">Standby</option>
                    </select>
                  </div>
                </div>
                
                <div className="text-sm text-gray-600">
                  Showing {filteredTrainsets.length} of {fleetStatus.trainsets.length} trainsets
                </div>
              </div>
            </div>

            {/* Trainset Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTrainsets.map(trainset => (
                <div key={trainset.trainset_id} className="bg-white rounded-lg shadow border hover:shadow-lg transition-shadow">
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        {getStatusIcon(trainset.status)}
                        <h3 className="ml-2 text-lg font-medium text-gray-900">{trainset.trainset_id}</h3>
                      </div>
                      <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(trainset.status)}`}>
                        {trainset.status}
                      </span>
                    </div>

                    {/* Reasoning */}
                    <div className="mb-4">
                      <p className="text-sm text-gray-600">{trainset.reason}</p>
                    </div>

                    {/* Alerts */}
                    {trainset.conflict_alerts.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-red-600 mb-2 flex items-center">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          Issues ({trainset.conflict_alerts.length})
                        </h4>
                        <div className="space-y-1">
                          {trainset.conflict_alerts.slice(0, 3).map((alert, idx) => (
                            <div key={idx} className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                              {alert}
                            </div>
                          ))}
                          {trainset.conflict_alerts.length > 3 && (
                            <div className="text-xs text-red-500">
                              +{trainset.conflict_alerts.length - 3} more
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="space-y-2 text-xs text-gray-500">
                      {trainset.metadata.fitness_certificate && (
                        <div className="flex items-center">
                          <FileText className="h-3 w-3 mr-2" />
                          FC: {trainset.metadata.fitness_certificate}
                        </div>
                      )}
                      {trainset.metadata.job_cards && (
                        <div className="flex items-center">
                          <Wrench className="h-3 w-3 mr-2" />
                          Jobs: {trainset.metadata.job_cards}
                        </div>
                      )}
                      {trainset.metadata.mileage && (
                        <div className="flex items-center">
                          <Eye className="h-3 w-3 mr-2" />
                          Mileage: {trainset.metadata.mileage}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button 
                        className="w-full text-sm text-metro-primary hover:text-metro-secondary font-medium"
                        onClick={() => {/* Navigate to detail view */}}
                      >
                        View Details & History
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredTrainsets.length === 0 && (
              <div className="text-center py-12">
                <Search className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No trainsets found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            )}

            {/* Inspection Summary */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Inspection Summary</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{fleetStatus.summary.fit}</div>
                    <div className="text-sm text-gray-600">Ready for Service</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{fleetStatus.summary.unfit}</div>
                    <div className="text-sm text-gray-600">Require Maintenance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{fleetStatus.summary.standby}</div>
                    <div className="text-sm text-gray-600">On Standby</div>
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

export default InspectionPortal;