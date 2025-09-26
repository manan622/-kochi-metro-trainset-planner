import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api, { trainsetAPI } from '../services/api';
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  Train,
  Settings,
  Database,
  Download,
  Trash2,
  Plus,
  Edit,
  X,
  Save,
  Shuffle
} from 'lucide-react';

const ManagementPortal = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataMessage, setDataMessage] = useState('');
  const [showAddTrainset, setShowAddTrainset] = useState(false);
  const [showGenerateDummy, setShowGenerateDummy] = useState(false);
  const [allTrainsets, setAllTrainsets] = useState([]);
  const [editingTrainset, setEditingTrainset] = useState(null);
  const [newTrainset, setNewTrainset] = useState({
    number: '',
    current_mileage: 0,
    stabling_bay: ''
  });
  const [dummyConfig, setDummyConfig] = useState({
    count: 5,
    prefix: 'TS'
  });

  useEffect(() => {
    fetchFleetStatus();
    fetchAllTrainsets();
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

  const fetchAllTrainsets = async () => {
    try {
      const data = await trainsetAPI.getAllTrainsets();
      setAllTrainsets(data);
    } catch (error) {
      console.error('Error fetching all trainsets:', error);
    }
  };

  const handleCreateTrainset = async (e) => {
    e.preventDefault();
    if (!newTrainset.number.trim()) {
      setDataMessage('Trainset number is required');
      return;
    }
    
    try {
      setDataLoading(true);
      setDataMessage('');
      await trainsetAPI.createTrainset(newTrainset);
      setDataMessage(`Successfully created trainset ${newTrainset.number}`);
      setNewTrainset({ number: '', current_mileage: 0, stabling_bay: '' });
      setShowAddTrainset(false);
      await Promise.all([fetchFleetStatus(), fetchAllTrainsets()]);
    } catch (error) {
      setDataMessage(`Error creating trainset: ${error.response?.data?.detail || error.message}`);
    } finally {
      setDataLoading(false);
    }
  };

  const handleGenerateDummy = async (e) => {
    e.preventDefault();
    try {
      setDataLoading(true);
      setDataMessage('');
      const response = await trainsetAPI.generateDummyTrainsets(dummyConfig.count, dummyConfig.prefix);
      setDataMessage(`Successfully generated ${response.total_count} dummy trainsets`);
      setShowGenerateDummy(false);
      await Promise.all([fetchFleetStatus(), fetchAllTrainsets()]);
    } catch (error) {
      setDataMessage(`Error generating dummy trainsets: ${error.response?.data?.detail || error.message}`);
    } finally {
      setDataLoading(false);
    }
  };

  const loadSampleData = async () => {
    try {
      setDataLoading(true);
      setDataMessage('');
      const response = await api.post('/api/data/load-sample?num_trainsets=25');
      setDataMessage(`Successfully loaded ${response.data.imported_trainsets} trainsets`);
      await fetchFleetStatus();
    } catch (error) {
      setDataMessage(`Error loading data: ${error.response?.data?.detail || error.message}`);
      console.error('Error loading sample data:', error);
    } finally {
      setDataLoading(false);
    }
  };

  const clearAllData = async () => {
    if (!window.confirm('Are you sure you want to clear all trainset data? This action cannot be undone.')) {
      return;
    }
    
    try {
      setDataLoading(true);
      setDataMessage('');
      await api.delete('/api/data/clear');
      setDataMessage('All trainset data cleared successfully');
      await fetchFleetStatus();
    } catch (error) {
      setDataMessage(`Error clearing data: ${error.response?.data?.detail || error.message}`);
      console.error('Error clearing data:', error);
    } finally {
      setDataLoading(false);
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

        {dataMessage && (
          <div className={`border rounded-md p-4 ${
            dataMessage.includes('Error') || dataMessage.includes('cleared')
              ? 'bg-red-50 border-red-200 text-red-800'
              : 'bg-green-50 border-green-200 text-green-800'
          }`}>
            <p>{dataMessage}</p>
          </div>
        )}

        {/* Enhanced Data Management Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Database className="h-5 w-5 mr-2 text-metro-primary" />
              Scalable Train Fleet Management
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Add individual trainsets, generate test data, or manage existing fleet
            </p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <button
                onClick={() => setShowAddTrainset(true)}
                disabled={dataLoading}
                className="bg-green-600 text-white px-4 py-3 rounded-md hover:bg-green-700 transition-colors flex items-center justify-center disabled:opacity-50"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add New Trainset
              </button>
              
              <button
                onClick={() => setShowGenerateDummy(true)}
                disabled={dataLoading}
                className="bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center disabled:opacity-50"
              >
                <Shuffle className="h-4 w-4 mr-2" />
                Generate Dummy Data
              </button>
              
              <button
                onClick={loadSampleData}
                disabled={dataLoading}
                className="bg-metro-primary text-white px-4 py-3 rounded-md hover:bg-metro-secondary transition-colors flex items-center justify-center disabled:opacity-50"
              >
                <Download className="h-4 w-4 mr-2" />
                {dataLoading ? 'Loading...' : 'Load Sample Data'}
              </button>
              
              <button
                onClick={clearAllData}
                disabled={dataLoading}
                className="bg-red-600 text-white px-4 py-3 rounded-md hover:bg-red-700 transition-colors flex items-center justify-center disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {dataLoading ? 'Processing...' : 'Clear All Data'}
              </button>
            </div>
            
            <div className="text-xs text-gray-500">
              <p><strong>Individual:</strong> Add trainsets one by one with custom details</p>
              <p><strong>Dummy:</strong> Generate realistic test data for development and testing</p>
              <p><strong>Sample:</strong> Load 25 trainsets with comprehensive maintenance records</p>
              <p><strong>Clear:</strong> Remove all trainset data and start fresh</p>
            </div>
          </div>
        </div>

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
          </>
        )}

        {/* Add Trainset Modal */}
        {showAddTrainset && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Add New Trainset</h3>
                <button onClick={() => setShowAddTrainset(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <form onSubmit={handleCreateTrainset}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Trainset Number *</label>
                    <input
                      type="text"
                      value={newTrainset.number}
                      onChange={(e) => setNewTrainset({...newTrainset, number: e.target.value})}
                      placeholder="e.g., TS-2025-001"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-metro-primary"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Mileage (km)</label>
                    <input
                      type="number"
                      value={newTrainset.current_mileage}
                      onChange={(e) => setNewTrainset({...newTrainset, current_mileage: parseFloat(e.target.value) || 0})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-metro-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Stabling Bay</label>
                    <input
                      type="text"
                      value={newTrainset.stabling_bay}
                      onChange={(e) => setNewTrainset({...newTrainset, stabling_bay: e.target.value})}
                      placeholder="e.g., Bay-01"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-metro-primary"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button type="button" onClick={() => setShowAddTrainset(false)} className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                    Cancel
                  </button>
                  <button type="submit" disabled={dataLoading} className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center">
                    <Plus className="h-4 w-4 mr-2" />
                    {dataLoading ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Generate Dummy Modal */}
        {showGenerateDummy && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Generate Dummy Trainsets</h3>
                <button onClick={() => setShowGenerateDummy(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <form onSubmit={handleGenerateDummy}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Number of Trainsets (1-50)</label>
                    <input
                      type="number"
                      value={dummyConfig.count}
                      onChange={(e) => setDummyConfig({...dummyConfig, count: parseInt(e.target.value) || 1})}
                      min="1" max="50"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-metro-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Prefix</label>
                    <input
                      type="text"
                      value={dummyConfig.prefix}
                      onChange={(e) => setDummyConfig({...dummyConfig, prefix: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-metro-primary"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button type="button" onClick={() => setShowGenerateDummy(false)} className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
                    Cancel
                  </button>
                  <button type="submit" disabled={dataLoading} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center">
                    <Shuffle className="h-4 w-4 mr-2" />
                    {dataLoading ? 'Generating...' : 'Generate'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ManagementPortal;