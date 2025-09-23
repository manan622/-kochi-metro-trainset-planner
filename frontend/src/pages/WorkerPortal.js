import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Calendar,
  Wrench,
  Users,
  MapPin,
  Timer,
  ClipboardList
} from 'lucide-react';

const WorkerPortal = () => {
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

  const getWorkAssignments = () => {
    if (!fleetStatus) return [];
    return fleetStatus.trainsets
      .filter(t => t.status === 'Unfit' || t.conflict_alerts.length > 0)
      .map(trainset => ({
        ...trainset,
        priority: trainset.conflict_alerts.some(alert => 
          alert.toLowerCase().includes('critical') || 
          alert.toLowerCase().includes('expired')
        ) ? 'high' : 'medium'
      }))
      .sort((a, b) => {
        if (a.priority === 'high' && b.priority !== 'high') return -1;
        if (b.priority === 'high' && a.priority !== 'high') return 1;
        return b.conflict_alerts.length - a.conflict_alerts.length;
      });
  };

  const getTasksByType = () => {
    const assignments = getWorkAssignments();
    const tasks = {
      maintenance: [],
      inspection: [],
      cleaning: []
    };

    assignments.forEach(trainset => {
      trainset.conflict_alerts.forEach(alert => {
        if (alert.toLowerCase().includes('maintenance') || alert.toLowerCase().includes('repair')) {
          tasks.maintenance.push({ ...trainset, task: alert });
        } else if (alert.toLowerCase().includes('certificate') || alert.toLowerCase().includes('inspection')) {
          tasks.inspection.push({ ...trainset, task: alert });
        } else if (alert.toLowerCase().includes('cleaning')) {
          tasks.cleaning.push({ ...trainset, task: alert });
        }
      });
    });

    return tasks;
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <ClipboardList className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <Layout title="Worker Portal">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  const workAssignments = getWorkAssignments();
  const tasksByType = getTasksByType();

  return (
    <Layout title="Worker Portal - Daily Tasks & Assignments">
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Today's Work Assignments</h2>
            <p className="text-gray-600">Maintenance tasks and operational assignments</p>
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
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <Wrench className="h-6 w-6 text-red-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Priority Tasks</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {workAssignments.filter(w => w.priority === 'high').length}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <ClipboardList className="h-6 w-6 text-yellow-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Total Tasks</p>
                    <p className="text-2xl font-semibold text-gray-900">{workAssignments.length}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Ready Trainsets</p>
                    <p className="text-2xl font-semibold text-gray-900">{fleetStatus.summary.fit}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <Users className="h-6 w-6 text-blue-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Team Status</p>
                    <p className="text-2xl font-semibold text-gray-900">Active</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Priority Work Assignments */}
            {workAssignments.length > 0 && (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center">
                    <Wrench className="h-5 w-5 mr-2 text-metro-primary" />
                    Work Assignments ({workAssignments.length})
                  </h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {workAssignments.map(trainset => (
                      <div 
                        key={trainset.trainset_id} 
                        className={`border rounded-lg p-4 ${getPriorityColor(trainset.priority)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center">
                            {getPriorityIcon(trainset.priority)}
                            <div className="ml-3">
                              <h4 className="font-medium text-gray-900">{trainset.trainset_id}</h4>
                              <p className="text-sm text-gray-600 mt-1">{trainset.reason}</p>
                            </div>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${trainset.priority === 'high' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'}`}>
                            {trainset.priority.toUpperCase()} PRIORITY
                          </span>
                        </div>
                        
                        {/* Task Details */}
                        <div className="mt-4 space-y-2">
                          {trainset.conflict_alerts.map((alert, idx) => (
                            <div key={idx} className="flex items-center text-sm">
                              <div className="w-2 h-2 bg-current rounded-full mr-3 opacity-60"></div>
                              <span>{alert}</span>
                            </div>
                          ))}
                        </div>

                        {/* Metadata */}
                        <div className="mt-4 pt-4 border-t border-current border-opacity-20">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                            {trainset.metadata.stabling_bay && (
                              <div className="flex items-center">
                                <MapPin className="h-3 w-3 mr-2" />
                                Location: {trainset.metadata.stabling_bay}
                              </div>
                            )}
                            {trainset.metadata.cleaning_slot && (
                              <div className="flex items-center">
                                <Timer className="h-3 w-3 mr-2" />
                                Cleaning: {trainset.metadata.cleaning_slot}
                              </div>
                            )}
                            {trainset.metadata.mileage && (
                              <div className="flex items-center">
                                <ClipboardList className="h-3 w-3 mr-2" />
                                Mileage: {trainset.metadata.mileage}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="mt-4 flex space-x-2">
                          <button className="text-xs bg-white text-gray-700 px-3 py-1 rounded border hover:bg-gray-50 transition-colors">
                            Start Task
                          </button>
                          <button className="text-xs bg-white text-gray-700 px-3 py-1 rounded border hover:bg-gray-50 transition-colors">
                            View Details
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Task Categories */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Maintenance Tasks */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center">
                    <Wrench className="h-5 w-5 mr-2 text-red-600" />
                    Maintenance ({tasksByType.maintenance.length})
                  </h3>
                </div>
                <div className="p-6">
                  {tasksByType.maintenance.length > 0 ? (
                    <div className="space-y-3">
                      {tasksByType.maintenance.slice(0, 5).map((task, idx) => (
                        <div key={idx} className="text-sm p-3 bg-red-50 rounded border">
                          <div className="font-medium text-red-900">{task.trainset_id}</div>
                          <div className="text-red-700 mt-1">{task.task}</div>
                        </div>
                      ))}
                      {tasksByType.maintenance.length > 5 && (
                        <div className="text-sm text-gray-500 text-center">
                          +{tasksByType.maintenance.length - 5} more tasks
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No maintenance tasks</p>
                  )}
                </div>
              </div>

              {/* Inspection Tasks */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2 text-blue-600" />
                    Inspection ({tasksByType.inspection.length})
                  </h3>
                </div>
                <div className="p-6">
                  {tasksByType.inspection.length > 0 ? (
                    <div className="space-y-3">
                      {tasksByType.inspection.slice(0, 5).map((task, idx) => (
                        <div key={idx} className="text-sm p-3 bg-blue-50 rounded border">
                          <div className="font-medium text-blue-900">{task.trainset_id}</div>
                          <div className="text-blue-700 mt-1">{task.task}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No inspection tasks</p>
                  )}
                </div>
              </div>

              {/* Cleaning Tasks */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center">
                    <Users className="h-5 w-5 mr-2 text-green-600" />
                    Cleaning ({tasksByType.cleaning.length})
                  </h3>
                </div>
                <div className="p-6">
                  {tasksByType.cleaning.length > 0 ? (
                    <div className="space-y-3">
                      {tasksByType.cleaning.slice(0, 5).map((task, idx) => (
                        <div key={idx} className="text-sm p-3 bg-green-50 rounded border">
                          <div className="font-medium text-green-900">{task.trainset_id}</div>
                          <div className="text-green-700 mt-1">{task.task}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No cleaning tasks</p>
                  )}
                </div>
              </div>
            </div>

            {/* No Tasks Message */}
            {workAssignments.length === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-4" />
                <h3 className="text-lg font-medium text-green-900 mb-2">All Tasks Complete!</h3>
                <p className="text-green-700">
                  No maintenance tasks assigned for today. All trainsets are in good condition.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default WorkerPortal;