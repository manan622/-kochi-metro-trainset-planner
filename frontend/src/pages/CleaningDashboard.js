import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Layout from '../components/Layout';
import api from '../services/api';
import {
  Camera,
  CheckCircle,
  Clock,
  AlertTriangle,
  User,
  Calendar,
  Star,
  Image as ImageIcon,
  Upload,
  RefreshCw,
  Users,
  ClipboardCheck,
  TrendingUp
} from 'lucide-react';

const CleaningDashboard = () => {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [cameraSupported, setCameraSupported] = useState(true);
  const [areaTypes] = useState([
    'Interior', 'Exterior', 'Seats', 'Floor', 'Windows', 
    'Handrails', 'Doors', 'Ceiling', 'Lighting', 'Air Vents'
  ]);
  const [selectedArea, setSelectedArea] = useState('Interior');
  const [photoEvaluations, setPhotoEvaluations] = useState([]);

  useEffect(() => {
    checkAuthentication();
    fetchDashboardData();
    fetchAssignments();
    checkCameraSupport();
  }, []);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('cleaning_token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Create a separate axios instance for cleaning API calls
      const cleaningApi = axios.create({
        baseURL: 'http://localhost:8001',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const response = await cleaningApi.get('/api/cleaning/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Authentication failed:', error);
      localStorage.removeItem('cleaning_token');
      navigate('/login');
    }
  };

  // Check camera support
  const checkCameraSupport = () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraSupported(false);
      setCameraError('Camera is not supported on this device/browser');
    }
  };

  // Create cleaning API instance
  const createCleaningApi = () => {
    const token = localStorage.getItem('cleaning_token');
    return axios.create({
      baseURL: 'http://localhost:8001',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
  };

  const fetchDashboardData = async () => {
    try {
      const cleaningApi = createCleaningApi();
      const response = await cleaningApi.get('/api/cleaning/dashboard/summary');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const cleaningApi = createCleaningApi();
      const response = await cleaningApi.get('/api/cleaning/assignments');
      setAssignments(response.data);
    } catch (error) {
      console.error('Error fetching assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPhotoEvaluations = async (assignmentId) => {
    try {
      const cleaningApi = createCleaningApi();
      const response = await cleaningApi.get(`/api/cleaning/assignments/${assignmentId}/photos`);
      setPhotoEvaluations(response.data);
    } catch (error) {
      console.error('Error fetching photo evaluations:', error);
    }
  };

  const updateAssignmentStatus = async (assignmentId, status, notes = null) => {
    try {
      const cleaningApi = createCleaningApi();
      const updateData = {
        status: status,
        actual_start: status === 'IN_PROGRESS' ? new Date().toISOString() : undefined,
        actual_end: status === 'COMPLETED' ? new Date().toISOString() : undefined,
        completion_notes: notes
      };

      await cleaningApi.put(`/api/cleaning/assignments/${assignmentId}`, updateData);

      // Refresh assignments
      fetchAssignments();
      fetchDashboardData();
    } catch (error) {
      console.error('Error updating assignment:', error);
    }
  };

  const startCameraAndCapture = async () => {
    setCameraError('');
    
    if (!cameraSupported) {
      setCameraError('Camera is not supported on this device');
      return;
    }

    try {
      // Request camera permission with better error handling
      const constraints = {
        video: {
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      console.log('Requesting camera access...');
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          // Wait a moment for the camera to initialize, then capture automatically
          setTimeout(() => {
            capturePhotoFromStream();
          }, 1000);
        };
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      
      let errorMessage = 'Unable to access camera. ';
      
      if (error.name === 'NotAllowedError') {
        errorMessage += 'Camera permission denied. Please allow camera access and try again.';
      } else if (error.name === 'NotFoundError') {
        errorMessage += 'No camera found on this device.';
      } else if (error.name === 'NotReadableError') {
        errorMessage += 'Camera is already in use by another application.';
      } else if (error.name === 'OverconstrainedError') {
        errorMessage += 'Camera constraints could not be satisfied.';
      } else {
        errorMessage += `Error: ${error.message}`;
      }
      
      setCameraError(errorMessage);
    }
  };

  const capturePhotoFromStream = () => {
    if (!videoRef.current || !canvasRef.current) {
      console.log('Camera not ready, retrying in 500ms...');
      setTimeout(() => capturePhotoFromStream(), 500);
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and create preview URL
    canvas.toBlob((blob) => {
      if (blob) {
        setCapturedPhoto(blob);
        const previewUrl = URL.createObjectURL(blob);
        setPhotoPreview(previewUrl);
        console.log('Photo captured automatically');
        // Stop the camera after capturing
        stopCameraStream();
      } else {
        alert('Failed to capture photo. Please try again.');
      }
    }, 'image/jpeg', 0.8);
  };

  const stopCameraStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  const stopCamera = () => {
    stopCameraStream();
    setCapturedPhoto(null);
    setPhotoPreview(null);
    setCameraError('');
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      alert('Camera not ready. Please try again.');
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and create preview URL
    canvas.toBlob((blob) => {
      if (blob) {
        setCapturedPhoto(blob);
        const previewUrl = URL.createObjectURL(blob);
        setPhotoPreview(previewUrl);
        console.log('Photo captured successfully');
      } else {
        alert('Failed to capture photo. Please try again.');
      }
    }, 'image/jpeg', 0.8);
  };

  const selectPhotoFromDevice = () => {
    fileInputRef.current.click();
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setCapturedPhoto(file);
      const previewUrl = URL.createObjectURL(file);
      setPhotoPreview(previewUrl);
      stopCamera(); // Stop camera if it was active
      console.log('File selected:', file.name);
    } else {
      alert('Please select a valid image file.');
    }
  };

  const uploadPhoto = async () => {
    if (!capturedPhoto || !selectedAssignment) {
      alert('Please capture a photo and select an assignment');
      return;
    }

    try {
      setUploadingPhoto(true);
      
      const formData = new FormData();
      formData.append('photo', capturedPhoto);
      formData.append('area_cleaned', selectedArea);

      console.log('Uploading photo for AI evaluation...');
      console.log('Assignment:', selectedAssignment.trainset_number);
      console.log('Area:', selectedArea);

      // Update headers for multipart form data
      const token = localStorage.getItem('cleaning_token');
      const response = await axios.post(
        `http://localhost:8001/api/cleaning/assignments/${selectedAssignment.id}/photos`,
        formData,
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Show AI evaluation result
      const evaluation = response.data;
      const isApproved = evaluation.is_approved ? '✅ APPROVED' : '❌ NEEDS REVIEW';
      
      alert(
        `🤖 AI Evaluation Complete!\n\n` +
        `📊 Quality Score: ${evaluation.ai_quality_score}%\n` +
        `⭐ Rating: ${evaluation.ai_quality_rating}\n` +
        `📝 Status: ${isApproved}\n\n` +
        `💬 AI Feedback:\n${evaluation.ai_feedback || 'No additional feedback provided.'}`
      );

      // Reset and refresh
      setCapturedPhoto(null);
      setPhotoPreview(null);
      stopCamera();
      fetchPhotoEvaluations(selectedAssignment.id);
      fetchDashboardData();

      console.log('Photo uploaded and evaluated successfully!');

    } catch (error) {
      console.error('Error uploading photo:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
      alert(`❌ Failed to upload photo:\n${errorMessage}\n\nPlease try again.`);
    } finally {
      setUploadingPhoto(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('cleaning_token');
    navigate('/login');
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'in_progress':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'verified':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <Layout title="Cleaning Dashboard">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-metro-primary"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Cleaning Team Dashboard">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Cleaning Dashboard</h2>
            <p className="text-gray-600">
              {user && `Welcome ${user.full_name} - ${dashboardData?.team_info?.team_name}`}
            </p>
          </div>
          <button
            onClick={logout}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Dashboard Summary */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <ClipboardCheck className="h-8 w-8 text-blue-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Today's Tasks</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.today_summary.total_assignments}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Completed</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.today_summary.completed}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-purple-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Completion Rate</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.today_summary.completion_rate}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Star className="h-8 w-8 text-yellow-600" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Avg Quality</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.quality_metrics.average_score}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Assignments List */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <ClipboardCheck className="h-5 w-5 mr-2 text-metro-primary" />
                Current Assignments
              </h3>
            </div>
            <div className="p-6">
              {assignments.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No assignments available</p>
              ) : (
                <div className="space-y-4">
                  {assignments.slice(0, 5).map((assignment) => (
                    <div
                      key={assignment.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedAssignment?.id === assignment.id
                          ? 'border-metro-primary bg-metro-primary/5'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setSelectedAssignment(assignment);
                        fetchPhotoEvaluations(assignment.id);
                      }}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            Trainset {assignment.trainset_number}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {assignment.cleaning_type} Cleaning
                          </p>
                          <p className="text-xs text-gray-500">
                            Scheduled: {new Date(assignment.scheduled_start).toLocaleString()}
                          </p>
                        </div>
                        <div className="flex flex-col items-end space-y-1">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(assignment.priority)}`}>
                            {assignment.priority}
                          </span>
                        </div>
                      </div>
                      
                      {assignment.status === 'PENDING' && (
                        <div className="mt-3 flex space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              updateAssignmentStatus(assignment.id, 'IN_PROGRESS');
                            }}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                          >
                            Start
                          </button>
                        </div>
                      )}
                      
                      {assignment.status === 'IN_PROGRESS' && (
                        <div className="mt-3 flex space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              const notes = prompt('Enter completion notes (optional):');
                              updateAssignmentStatus(assignment.id, 'COMPLETED', notes);
                            }}
                            className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700"
                          >
                            Complete
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Camera and Photo Upload */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Camera className="h-5 w-5 mr-2 text-metro-primary" />
                Photo Capture & Evaluation
              </h3>
            </div>
            <div className="p-6">
              {!selectedAssignment ? (
                <p className="text-gray-500 text-center py-8">
                  Select an assignment to capture photos
                </p>
              ) : (
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-600 mb-2">
                      Assignment: Trainset {selectedAssignment.trainset_number}
                    </p>
                    
                    {/* Area Selection */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Area to Clean:
                      </label>
                      <select
                        value={selectedArea}
                        onChange={(e) => setSelectedArea(e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-metro-primary"
                      >
                        {areaTypes.map((area) => (
                          <option key={area} value={area}>{area}</option>
                        ))}
                      </select>
                    </div>

                    {/* Camera Error Display */}
                    {cameraError && (
                      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm text-red-700">{cameraError}</p>
                        {cameraError.includes('permission') && (
                          <div className="mt-2 text-xs text-red-600">
                            <p>To enable camera access:</p>
                            <ul className="list-disc list-inside mt-1">
                              <li>Click the camera icon in your browser's address bar</li>
                              <li>Select "Allow" for camera access</li>
                              <li>Refresh the page if needed</li>
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Camera Controls */}
                    {!cameraActive && !capturedPhoto && (
                      <div className="space-y-2">
                        {cameraSupported ? (
                          <button
                            onClick={startCameraAndCapture}
                            disabled={!!cameraError}
                            className="bg-metro-primary text-white px-4 py-2 rounded-md hover:bg-metro-secondary transition-colors flex items-center mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Camera className="h-4 w-4 mr-2" />
                            {cameraError ? 'Camera Unavailable' : '📸 Take Photo'}
                          </button>
                        ) : (
                          <p className="text-red-500 text-sm">Camera not supported on this device</p>
                        )}
                        <p className="text-xs text-gray-500">or</p>
                        <button
                          onClick={selectPhotoFromDevice}
                          className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors flex items-center mx-auto"
                        >
                          <ImageIcon className="h-4 w-4 mr-2" />
                          Select from Device
                        </button>
                      </div>
                    )}

                    {/* Camera View - Hidden, only for capture */}
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="hidden"
                    />

                    {/* Photo Preview and Upload */}
                    {capturedPhoto && (
                      <div className="space-y-4">
                        {/* Photo Preview */}
                        {photoPreview && (
                          <div className="text-center">
                            <img 
                              src={photoPreview} 
                              alt="Captured photo preview" 
                              className="max-w-md mx-auto rounded-lg border-2 border-green-400"
                              style={{ maxHeight: '300px' }}
                            />
                          </div>
                        )}
                        
                        <div className="text-center">
                          <p className="text-sm font-medium text-gray-900 mb-1">
                            📷 Photo ready for: <span className="text-metro-primary">{selectedArea}</span>
                          </p>
                          <p className="text-xs text-gray-500 mb-4">
                            AI will evaluate cleaning quality and provide feedback
                          </p>
                        </div>
                        
                        <div className="flex justify-center space-x-3">
                          <button
                            onClick={uploadPhoto}
                            disabled={uploadingPhoto}
                            className="bg-metro-primary text-white px-6 py-3 rounded-md hover:bg-metro-secondary transition-colors disabled:opacity-50 font-medium flex items-center"
                          >
                            {uploadingPhoto ? (
                              <>
                                <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                                Processing...
                              </>
                            ) : (
                              <>
                                <Upload className="h-4 w-4 mr-2" />
                                🤖 AI Evaluate
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => {
                              setCapturedPhoto(null);
                              setPhotoPreview(null);
                            }}
                            className="bg-gray-600 text-white px-4 py-3 rounded-md hover:bg-gray-700 transition-colors"
                            disabled={uploadingPhoto}
                          >
                            Retake
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Photo Evaluations */}
                  {photoEvaluations.length > 0 && (
                    <div className="mt-6">
                      <h4 className="font-medium text-gray-900 mb-3">Recent Photos</h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {photoEvaluations.map((photo) => (
                          <div key={photo.id} className="flex justify-between items-center p-2 border rounded">
                            <div className="text-sm">
                              <p className="font-medium">{photo.area_cleaned}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(photo.photo_timestamp).toLocaleString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium">
                                Score: {photo.ai_quality_score}%
                              </p>
                              <p className={`text-xs px-2 py-1 rounded ${
                                photo.is_approved ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                              }`}>
                                {photo.is_approved ? 'Approved' : 'Needs Review'}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Hidden elements */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </Layout>
  );
};

export default CleaningDashboard;