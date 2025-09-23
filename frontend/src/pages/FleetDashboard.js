import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  Train, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  BarChart3,
  RefreshCw,
  Eye,
  Filter,
  Search,
  TrendingUp
} from 'lucide-react';

const FleetDashboard = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('cards'); // 'cards' or 'list'
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchFleetStatus();
  }, [selectedDate]);

  const fetchFleetStatus = async () => {
    try {
      setLoading(true);
      setError('');
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
        return 'status-fit';
      case 'unfit':
        return 'status-unfit';
      case 'standby':
        return 'status-standby';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredTrainsets = fleetStatus?.trainsets?.filter(trainset => {
    const matchesStatus = filterStatus === 'all' || trainset.status.toLowerCase() === filterStatus;
    const matchesSearch = trainset.trainset_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  }) || [];

  const handleTrainsetClick = (trainsetId) => {
    navigate(`/trainset/${trainsetId}`);
  };

  const TrainsetCard = ({ trainset }) => (
    <div 
      className="bg-white rounded-lg shadow border hover:shadow-lg transition-all duration-200 cursor-pointer card-hover"
      onClick={() => handleTrainsetClick(trainset.trainset_id)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Train className="h-6 w-6 text-metro-primary mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">{trainset.trainset_id}</h3>
          </div>
          <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getStatusColor(trainset.status)}`}>
            {trainset.status}
          </span>
        </div>

        {/* Status Icon and Reasoning */}
        <div className="flex items-start mb-4">
          {getStatusIcon(trainset.status)}
          <div className="ml-3 flex-1">
            <p className="text-sm text-gray-700 leading-relaxed">{trainset.reason}</p>
          </div>
        </div>

        {/* Alerts */}
        {trainset.conflict_alerts.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {trainset.conflict_alerts.slice(0, 3).map((alert, idx) => (
                <span 
                  key={idx} 
                  className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded"
                >
                  {alert}
                </span>
              ))}
              {trainset.conflict_alerts.length > 3 && (
                <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                  +{trainset.conflict_alerts.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Metadata Summary */}
        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 border-t border-gray-100 pt-4">
          <div>
            <span className="font-medium">Mileage:</span>
            <span className="ml-1">{trainset.metadata.mileage || 'N/A'}</span>
          </div>
          <div>
            <span className="font-medium">Bay:</span>
            <span className="ml-1">{trainset.metadata.stabling_bay || 'N/A'}</span>
          </div>
        </div>

        {/* Action */}
        <div className="mt-4 flex items-center justify-between">
          <div className="text-xs text-gray-400">
            Click for details
          </div>
          <Eye className="h-4 w-4 text-gray-400" />
        </div>
      </div>
    </div>
  );

  const TrainsetListItem = ({ trainset }) => (
    <div 
      className="bg-white rounded-lg shadow border hover:shadow-md transition-all duration-200 cursor-pointer"
      onClick={() => handleTrainsetClick(trainset.trainset_id)}
    >
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center flex-1">
            <Train className="h-5 w-5 text-metro-primary mr-3 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3">
                <h3 className="text-sm font-semibold text-gray-900">{trainset.trainset_id}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(trainset.status)}`}>
                  {trainset.status}
                </span>
                {trainset.conflict_alerts.length > 0 && (
                  <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                    {trainset.conflict_alerts.length} alerts
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-600 mt-1 truncate">{trainset.reason}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>{trainset.metadata.mileage || 'N/A'}</span>
            <span>{trainset.metadata.stabling_bay || 'N/A'}</span>
            <Eye className="h-4 w-4 text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <Layout title="Fleet Dashboard">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Fleet Dashboard - Trainset Overview">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Fleet Dashboard</h2>
            <p className="text-gray-600">Real-time trainset status and induction planning</p>
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
              disabled={loading}
              className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors flex items-center disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-red-800">{error}</p>
                <button 
                  onClick={fetchFleetStatus}
                  className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        )}

        {fleetStatus && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <Train className="h-8 w-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Fleet</p>
                    <p className="text-2xl font-bold text-gray-900">{fleetStatus.summary.total_trainsets}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Ready for Service</p>
                    <p className="text-2xl font-bold text-green-600">{fleetStatus.summary.fit}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-xs text-gray-500">
                    {((fleetStatus.summary.fit / fleetStatus.summary.total_trainsets) * 100).toFixed(1)}% of fleet
                  </span>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Maintenance Required</p>
                    <p className="text-2xl font-bold text-red-600">{fleetStatus.summary.unfit}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-xs text-gray-500">
                    {fleetStatus.summary.total_alerts} active alerts
                  </span>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">On Standby</p>
                    <p className="text-2xl font-bold text-yellow-600">{fleetStatus.summary.standby}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-xs text-gray-500">Available reserve</span>
                </div>
              </div>
            </div>

            {/* Filters and Controls */}
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
                
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setViewMode('cards')}
                      className={`p-2 rounded ${viewMode === 'cards' ? 'bg-metro-primary text-white' : 'bg-gray-100 text-gray-600'}`}
                    >
                      <BarChart3 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-2 rounded ${viewMode === 'list' ? 'bg-metro-primary text-white' : 'bg-gray-100 text-gray-600'}`}
                    >
                      <TrendingUp className="h-4 w-4" />
                    </button>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    {filteredTrainsets.length} of {fleetStatus.trainsets.length} trainsets
                  </div>
                </div>
              </div>
            </div>

            {/* Trainsets Grid/List */}
            {filteredTrainsets.length > 0 ? (
              <div className={`${viewMode === 'cards' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-3'}`}>
                {filteredTrainsets.map(trainset => 
                  viewMode === 'cards' ? (
                    <TrainsetCard key={trainset.trainset_id} trainset={trainset} />
                  ) : (
                    <TrainsetListItem key={trainset.trainset_id} trainset={trainset} />
                  )
                )}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <Search className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No trainsets found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default FleetDashboard;