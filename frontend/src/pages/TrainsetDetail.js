import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { trainsetAPI } from '../services/api';
import { 
  Train, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Calendar,
  ArrowLeft,
  FileText,
  Wrench,
  Star,
  BarChart3,
  MapPin,
  Users,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Info,
  Camera,
  UserCheck
} from 'lucide-react';

const TrainsetDetail = () => {
  const { trainsetId } = useParams();
  const navigate = useNavigate();
  const [trainset, setTrainset] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [cleaningInfo, setCleaningInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedSections, setExpandedSections] = useState({
    reasoning: true,
    certificates: false,
    jobCards: false,
    branding: false,
    mileage: false,
    cleaning: false
  });

  useEffect(() => {
    fetchTrainsetDetails();
  }, [trainsetId]);

  const fetchTrainsetDetails = async () => {
    try {
      setLoading(true);
      setError('');
      
      console.log('Fetching trainset details for:', trainsetId);
      
      // Determine if trainsetId is a number (ID) or string (trainset number)
      const isNumericId = /^\d+$/.test(trainsetId);
      console.log('Is numeric ID:', isNumericId);
      
      let trainsetData;
      try {
        if (isNumericId) {
          // If it's a numeric ID, use getTrainsetDetail
          console.log('Fetching by ID:', trainsetId);
          trainsetData = await trainsetAPI.getTrainsetDetail(trainsetId);
        } else {
          // If it's a trainset number (like TS-2003), use getTrainsetByNumber
          console.log('Fetching by number:', trainsetId);
          trainsetData = await trainsetAPI.getTrainsetByNumber(trainsetId);
        }
        console.log('Trainset data loaded:', trainsetData.number);
      } catch (err) {
        console.error('Error fetching trainset data:', err);
        throw new Error(`Failed to fetch trainset information: ${err.response?.data?.detail || err.message}`);
      }
      
      // Use the trainset's actual ID for evaluation (not the URL param)
      let evaluationData;
      try {
        console.log('Fetching evaluation for ID:', trainsetData.id);
        evaluationData = await trainsetAPI.getTrainsetEvaluation(trainsetData.id);
        console.log('Evaluation data loaded:', evaluationData.status);
      } catch (err) {
        console.error('Error fetching evaluation data:', err);
        throw new Error(`Failed to fetch trainset evaluation: ${err.response?.data?.detail || err.message}`);
      }
      
      // Fetch cleaning information
      let cleaningData = null;
      try {
        console.log('Fetching cleaning info for ID:', trainsetData.id);
        const response = await fetch(`/api/trainsets/${trainsetData.id}/cleaning`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        if (response.ok) {
          cleaningData = await response.json();
          console.log('Cleaning data loaded:', cleaningData);
        }
      } catch (err) {
        console.warn('Could not fetch cleaning data:', err);
        // Don't throw error for cleaning data as it's optional
      }
      
      setTrainset(trainsetData);
      setEvaluation(evaluationData);
      setCleaningInfo(cleaningData);
      console.log('All data loaded successfully');
    } catch (error) {
      const errorMessage = error.message || 'Failed to fetch trainset details';
      setError(errorMessage);
      console.error('Error in fetchTrainsetDetails:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'fit':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'unfit':
        return <AlertTriangle className="h-6 w-6 text-red-600" />;
      case 'standby':
        return <Clock className="h-6 w-6 text-yellow-600" />;
      default:
        return <Clock className="h-6 w-6 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const Section = ({ title, icon: Icon, expanded, onToggle, children, count = null }) => (
    <div className="bg-white rounded-lg shadow border">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center">
          <Icon className="h-5 w-5 text-metro-primary mr-3" />
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {count !== null && (
            <span className="ml-2 bg-gray-100 text-gray-600 text-sm px-2 py-1 rounded">
              {count}
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </button>
      {expanded && (
        <div className="px-6 pb-6 border-t border-gray-100">
          {children}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <Layout title="Trainset Details">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  if (error || !trainset) {
    return (
      <Layout title="Trainset Details">
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-600 mb-4" />
          <h3 className="text-lg font-medium text-red-900 mb-2">Error Loading Trainset</h3>
          <p className="text-red-700 mb-6">{error || 'Trainset not found'}</p>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-2 inline" />
              Back to Dashboard
            </button>
            <button
              onClick={fetchTrainsetDetails}
              className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2 inline" />
              Try Again
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`Trainset ${trainset.number} - Detailed View`}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-md transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
            <div className="flex items-center">
              <Train className="h-8 w-8 text-metro-primary mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Trainset {trainset.number}</h1>
                <p className="text-gray-600">Detailed information and analysis</p>
              </div>
            </div>
          </div>
          
          <button
            onClick={fetchTrainsetDetails}
            disabled={loading}
            className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors flex items-center disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Status Overview */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                {getStatusIcon(trainset.status)}
                <div className="ml-4">
                  <h2 className="text-xl font-semibold text-gray-900">Current Status</h2>
                  <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full border mt-2 ${getStatusColor(trainset.status)}`}>
                    {trainset.status}
                  </span>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm font-medium text-gray-900">
                  {formatDate(trainset.updated_at) || formatDate(trainset.created_at)}
                </p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <BarChart3 className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Current Mileage</p>
                <p className="text-lg font-semibold text-gray-900">
                  {trainset.current_mileage ? `${trainset.current_mileage.toLocaleString()} km` : 'N/A'}
                </p>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <MapPin className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Stabling Bay</p>
                <p className="text-lg font-semibold text-gray-900">{trainset.stabling_bay || 'N/A'}</p>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <FileText className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Certificates</p>
                <p className="text-lg font-semibold text-gray-900">{trainset.fitness_certificates?.length || 0}</p>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Wrench className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Job Cards</p>
                <p className="text-lg font-semibold text-gray-900">{trainset.job_cards?.length || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Explainable Reasoning */}
        {evaluation && (
          <Section
            title="Status Reasoning & Analysis"
            icon={Info}
            expanded={expandedSections.reasoning}
            onToggle={() => toggleSection('reasoning')}
          >
            <div className="mt-4 space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Current Assessment</h4>
                <p className="text-blue-800">{evaluation.reason}</p>
              </div>
              
              {evaluation.conflict_alerts.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h4 className="font-medium text-red-900 mb-2">Active Alerts</h4>
                  <div className="space-y-2">
                    {evaluation.conflict_alerts.map((alert, idx) => (
                      <div key={idx} className="flex items-center text-red-800">
                        <AlertTriangle className="h-4 w-4 mr-2 flex-shrink-0" />
                        <span>{alert}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {evaluation.metadata && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(evaluation.metadata).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3">
                      <h5 className="text-sm font-medium text-gray-700 capitalize mb-1">
                        {key.replace('_', ' ')}
                      </h5>
                      <p className="text-sm text-gray-900">{value}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Fitness Certificates */}
        <Section
          title="Fitness Certificates"
          icon={FileText}
          expanded={expandedSections.certificates}
          onToggle={() => toggleSection('certificates')}
          count={trainset.fitness_certificates?.length}
        >
          <div className="mt-4">
            {trainset.fitness_certificates?.length > 0 ? (
              <div className="space-y-4">
                {trainset.fitness_certificates.map((cert) => (
                  <div key={cert.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{cert.certificate_type}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        cert.status === 'Valid' ? 'bg-green-100 text-green-800' : 
                        cert.status === 'Expired' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {cert.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Certificate #:</span>
                        <span className="ml-1">{cert.certificate_number}</span>
                      </div>
                      <div>
                        <span className="font-medium">Issue Date:</span>
                        <span className="ml-1">{formatDate(cert.issue_date)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Expiry Date:</span>
                        <span className="ml-1">{formatDate(cert.expiry_date)}</span>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      <span className="font-medium">Authority:</span>
                      <span className="ml-1">{cert.issuing_authority}</span>
                    </div>
                    {cert.notes && (
                      <div className="mt-2 text-sm text-gray-600">
                        <span className="font-medium">Notes:</span>
                        <span className="ml-1">{cert.notes}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No fitness certificates on record</p>
            )}
          </div>
        </Section>

        {/* Job Cards */}
        <Section
          title="Job Cards"
          icon={Wrench}
          expanded={expandedSections.jobCards}
          onToggle={() => toggleSection('jobCards')}
          count={trainset.job_cards?.length}
        >
          <div className="mt-4">
            {trainset.job_cards?.length > 0 ? (
              <div className="space-y-4">
                {trainset.job_cards.map((job) => (
                  <div key={job.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{job.job_card_number}</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          job.priority === 'High' ? 'bg-red-100 text-red-800' :
                          job.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {job.priority}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          job.status === 'Open' ? 'bg-red-100 text-red-800' :
                          job.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {job.status}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 mb-3">{job.description}</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Created:</span>
                        <span className="ml-1">{formatDate(job.created_date)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Due Date:</span>
                        <span className="ml-1">{formatDate(job.due_date)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Assigned:</span>
                        <span className="ml-1">{job.assigned_to || 'Unassigned'}</span>
                      </div>
                    </div>
                    {job.estimated_hours && (
                      <div className="mt-2 text-sm text-gray-600">
                        <span className="font-medium">Estimated Hours:</span>
                        <span className="ml-1">{job.estimated_hours}h</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No job cards on record</p>
            )}
          </div>
        </Section>

        {/* Branding Priorities */}
        {trainset.branding_priorities?.length > 0 && (
          <Section
            title="Branding Priorities"
            icon={Star}
            expanded={expandedSections.branding}
            onToggle={() => toggleSection('branding')}
            count={trainset.branding_priorities?.length}
          >
            <div className="mt-4 space-y-4">
              {trainset.branding_priorities.map((brand) => (
                <div key={brand.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{brand.brand_name}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      brand.priority_level === 'High' ? 'bg-red-100 text-red-800' :
                      brand.priority_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {brand.priority_level} Priority
                    </span>
                  </div>
                  {brand.campaign_name && (
                    <p className="text-sm text-gray-700 mb-2">Campaign: {brand.campaign_name}</p>
                  )}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Contract Period:</span>
                      <span className="ml-1">
                        {formatDate(brand.contract_start_date)} - {formatDate(brand.contract_end_date)}
                      </span>
                    </div>
                    {brand.revenue_impact && (
                      <div>
                        <span className="font-medium">Revenue Impact:</span>
                        <span className="ml-1">₹{brand.revenue_impact.toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Mileage Records */}
        {trainset.mileage_records?.length > 0 && (
          <Section
            title="Recent Mileage Records"
            icon={BarChart3}
            expanded={expandedSections.mileage}
            onToggle={() => toggleSection('mileage')}
            count={trainset.mileage_records?.length}
          >
            <div className="mt-4">
              <div className="space-y-3">
                {trainset.mileage_records.slice(0, 5).map((record) => (
                  <div key={record.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <span className="text-sm font-medium text-gray-900">
                        {formatDate(record.date)}
                      </span>
                      {record.route && (
                        <span className="ml-2 text-sm text-gray-600">({record.route})</span>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {record.daily_mileage} km
                      </div>
                      <div className="text-xs text-gray-500">
                        Total: {record.cumulative_mileage.toLocaleString()} km
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Section>
        )}

        {/* Cleaning Slots */}
        {trainset.cleaning_slots?.length > 0 && (
          <Section
            title="Cleaning Schedule"
            icon={Users}
            expanded={expandedSections.cleaning}
            onToggle={() => toggleSection('cleaning')}
            count={trainset.cleaning_slots?.length}
          >
            <div className="mt-4 space-y-4">
              {trainset.cleaning_slots.map((slot) => (
                <div key={slot.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{slot.cleaning_type} Cleaning</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      slot.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      slot.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {slot.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Date:</span>
                      <span className="ml-1">{formatDate(slot.slot_date)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Bay:</span>
                      <span className="ml-1">{slot.bay_number}</span>
                    </div>
                    <div>
                      <span className="font-medium">Crew:</span>
                      <span className="ml-1">{slot.assigned_crew || 'TBD'}</span>
                    </div>
                  </div>
                  {slot.estimated_duration && (
                    <div className="mt-2 text-sm text-gray-600">
                      <span className="font-medium">Duration:</span>
                      <span className="ml-1">{slot.estimated_duration} minutes</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* AI-Powered Cleaning Evaluations */}
        {cleaningInfo && (
          <Section
            title="Cleaning Team Assignments & AI Evaluations"
            icon={Camera}
            expanded={expandedSections.cleaning}
            onToggle={() => toggleSection('cleaning')}
            count={cleaningInfo.recent_assignments?.length}
          >
            <div className="mt-4">
              {/* Quality Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Cleaning Quality Summary</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-metro-primary">
                      {cleaningInfo.quality_summary?.average_score || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Average AI Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {cleaningInfo.quality_summary?.approved_photos || 0}
                    </div>
                    <div className="text-sm text-gray-600">Approved Photos</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {cleaningInfo.quality_summary?.total_photos || 0}
                    </div>
                    <div className="text-sm text-gray-600">Total Photos</div>
                  </div>
                </div>
              </div>

              {/* Recent Assignments */}
              {cleaningInfo.recent_assignments?.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Recent Cleaning Assignments</h4>
                  <div className="space-y-3">
                    {cleaningInfo.recent_assignments.map((assignment) => (
                      <div key={assignment.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <UserCheck className="h-4 w-4 text-metro-primary mr-2" />
                            <span className="font-medium text-gray-900">{assignment.team_name}</span>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            assignment.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                            assignment.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {assignment.status}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Type:</span>
                            <span className="ml-1">{assignment.cleaning_type}</span>
                          </div>
                          <div>
                            <span className="font-medium">Assigned:</span>
                            <span className="ml-1">{formatDate(assignment.assigned_date)}</span>
                          </div>
                          {assignment.completed_date && (
                            <div>
                              <span className="font-medium">Completed:</span>
                              <span className="ml-1">{formatDate(assignment.completed_date)}</span>
                            </div>
                          )}
                        </div>
                        {assignment.completion_notes && (
                          <div className="mt-2 text-sm text-gray-600">
                            <span className="font-medium">Notes:</span>
                            <span className="ml-1">{assignment.completion_notes}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Photos with AI Evaluation */}
              {cleaningInfo.recent_photos?.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Recent AI Photo Evaluations</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {cleaningInfo.recent_photos.slice(0, 6).map((photo) => (
                      <div key={photo.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <Camera className="h-4 w-4 text-metro-primary mr-2" />
                            <span className="font-medium text-gray-900">{photo.area_cleaned}</span>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            photo.is_approved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {photo.is_approved ? 'Approved' : 'Needs Review'}
                          </span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">AI Quality Score:</span>
                            <span className={`font-medium ${
                              photo.ai_quality_score >= 90 ? 'text-green-600' :
                              photo.ai_quality_score >= 70 ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {photo.ai_quality_score}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Rating:</span>
                            <span className="font-medium text-gray-900">
                              {photo.ai_quality_rating}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Team:</span>
                            <span className="text-gray-900">{photo.team_name}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Cleaner:</span>
                            <span className="text-gray-900">{photo.cleaner_name}</span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {formatDate(photo.photo_timestamp)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Link to Cleaning Dashboard */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="bg-metro-primary/5 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h5 className="font-medium text-gray-900">Cleaning Team Dashboard</h5>
                      <p className="text-sm text-gray-600 mt-1">
                        Access the dedicated cleaning team interface for photo capture and AI evaluation
                      </p>
                    </div>
                    <button
                      onClick={() => window.open('/login', '_blank')}
                      className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors flex items-center"
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      Open Cleaning Dashboard
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Section>
        )}
      </div>
    </Layout>
  );
};

export default TrainsetDetail;