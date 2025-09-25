import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  Plus,
  Train,
  Play,
  Square
} from 'lucide-react';

const InspectionPortal = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [myInspections, setMyInspections] = useState([]);
  const [availableTrainsets, setAvailableTrainsets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchFleetStatus();
    fetchMyInspections();
    fetchAvailableTrainsets();
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

  const fetchMyInspections = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/inspections/my', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMyInspections(data);
      }
    } catch (error) {
      console.error('Error fetching inspections:', error);
    }
  };

  const fetchAvailableTrainsets = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/trainsets/available', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAvailableTrainsets(data);
      }
    } catch (error) {
      console.error('Error fetching trainsets:', error);
    }
  };

  const handleCreateInspection = () => {
    // Placeholder for create inspection functionality
    const trainsetId = prompt('Enter Trainset ID for inspection:');
    const description = prompt('Enter inspection description:');
    
    if (trainsetId && description) {
      // Create inspection logic here
      const newInspection = {
        id: Date.now(),
        inspection_number: `INS-${Date.now()}`,
        trainset_number: trainsetId,
        inspection_type: 'SCHEDULED',
        status: 'PENDING',
        description: description,
        scheduled_date: new Date().toISOString(),
        estimated_duration: 60
      };
      
      setMyInspections([newInspection, ...myInspections]);
      alert('Inspection created successfully!');
    }
  };

  const handleAddTrainset = () => {
    // Placeholder for add trainset functionality
    const trainsetNumber = prompt('Enter Trainset Number (e.g., TS-2025):');
    const reason = prompt('Enter reason for addition:');
    
    if (trainsetNumber && reason) {
      // Add trainset logic here
      const newTrainset = {
        id: Date.now(),
        number: trainsetNumber,
        current_mileage: 0,
        stabling_bay: '',
        description: reason
      };
      
      setAvailableTrainsets([...availableTrainsets, newTrainset]);
      alert('Trainset added successfully!');
    }
  };

  const handleStartInspection = async (inspectionId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/inspections/${inspectionId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        fetchMyInspections();
        alert('Inspection started!');
      } else {
        const error = await response.json();
        alert(`Error starting inspection: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error starting inspection:', error);
      alert('Error starting inspection');
    }
  };

  const handleCompleteInspection = async (inspectionId) => {
    const notes = prompt('Enter completion notes (optional):');
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/inspections/${inspectionId}/complete?completion_notes=${encodeURIComponent(notes || '')}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        fetchMyInspections();
        alert('Inspection completed!');
      } else {
        const error = await response.json();
        alert(`Error completing inspection: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error completing inspection:', error);
      alert('Error completing inspection');
    }
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
    <Layout title="Inspection Portal">
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Inspection Portal</h2>
            <p className="text-gray-600">Manage inspections and trainset assessments</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={handleAddTrainset}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Train className="h-4 w-4 mr-2" />
              Add Trainset for Mid-Day Check
            </button>
            <button
              onClick={handleCreateInspection}
              className="flex items-center px-4 py-2 bg-metro-primary text-white rounded-md hover:bg-metro-secondary transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Inspection
            </button>
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

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-metro-primary text-metro-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Fleet Overview
            </button>
            <button
              onClick={() => setActiveTab('my-inspections')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'my-inspections'
                  ? 'border-metro-primary text-metro-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Inspections ({myInspections.length})
            </button>
          </nav>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Fleet Overview Tab */}
        {activeTab === 'overview' && fleetStatus && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Fleet Summary</h3>
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

            {/* Available Trainsets */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Available Trainsets ({availableTrainsets.length})</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availableTrainsets.slice(0, 6).map((trainset) => (
                    <div key={trainset.id} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900">{trainset.number}</h4>
                      <p className="text-sm text-gray-600">Mileage: {trainset.current_mileage} km</p>
                      <p className="text-sm text-gray-600">Bay: {trainset.stabling_bay || 'Not assigned'}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* My Inspections Tab */}
        {activeTab === 'my-inspections' && (
          <div className="space-y-6">
            {myInspections.length === 0 ? (
              <div className="text-center py-12">
                <h3 className="mt-2 text-sm font-medium text-gray-900">No inspections assigned</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create a new inspection to get started.
                </p>
              </div>
            ) : (
              <div className="grid gap-6">
                {myInspections.map((inspection) => (
                  <div key={inspection.id} className="bg-white rounded-lg shadow border border-gray-200 p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {inspection.inspection_number}
                          </h3>
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {inspection.status ? inspection.status.replace('_', ' ') : 'PENDING'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">Trainset: {inspection.trainset_number}</p>
                        <p className="text-sm text-gray-600">Type: {inspection.inspection_type ? inspection.inspection_type.replace('_', ' ') : 'Scheduled'}</p>
                      </div>
                      
                      <div className="flex space-x-2">
                        {(!inspection.status || inspection.status === 'PENDING') && (
                          <button
                            onClick={() => handleStartInspection(inspection.id)}
                            className="flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                          >
                            <Play className="h-3 w-3 mr-1" />
                            Start
                          </button>
                        )}
                        {inspection.status === 'IN_PROGRESS' && (
                          <button
                            onClick={() => handleCompleteInspection(inspection.id)}
                            className="flex items-center px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                          >
                            <Square className="h-3 w-3 mr-1" />
                            Complete
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-sm text-gray-700">{inspection.description}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Scheduled:</span>
                        <p className="font-medium">
                          {new Date(inspection.scheduled_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Duration:</span>
                        <p className="font-medium">
                          {inspection.estimated_duration || 'N/A'} min
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Location:</span>
                        <p className="font-medium">{inspection.location || 'TBD'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default InspectionPortal;