'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { BarChart3, Activity, Calendar, ArrowLeft, Loader2, Maximize2, X, RefreshCw } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Pie, Bar, Scatter, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface GraphData {
  chart_id: string;
  title: string;
  description: string;
  figure: any;
  meta: any;
}

export default function AnalyticsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [graphs, setGraphs] = useState<GraphData[]>([]);
  const [loadingGraphs, setLoadingGraphs] = useState(true);
  const [error, setError] = useState('');
  const [expandedGraph, setExpandedGraph] = useState<GraphData | null>(null);
  const [showDebugInfo, setShowDebugInfo] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && isAuthenticated) {
      fetchGraphs();
    }
  }, [isAuthenticated, authLoading, router]);

  const fetchGraphs = async () => {
    try {
      setLoadingGraphs(true);
      setError('');
      const accessToken = localStorage.getItem('access_token');
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/graphs/overview`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }

      const data = await response.json();
      console.log('Analytics data received:', data);
      setGraphs(data);
    } catch (err) {
      console.error('Error fetching graphs:', err);
      setError('Failed to load analytics. Please try again.');
    } finally {
      setLoadingGraphs(false);
    }
  };

  const renderChart = (graph: GraphData) => {
    const chartData = graph.figure?.data || [];
    const chartLayout = graph.figure?.layout || {};
    const annotations = chartLayout?.annotations || [];
    
    console.log(`Rendering chart ${graph.chart_id}:`, {
      chartData,
      annotations,
      hasData: chartData && chartData.length > 0
    });

    // Check if this is an empty figure (has annotations but no data)
    if (annotations.length > 0 && (!chartData || chartData.length === 0)) {
      const message = annotations[0]?.text || 'No data available yet';
      return (
        <div className="h-full flex items-center justify-center">
          <div className="text-center p-6">
            <Activity className="w-16 h-16 text-blue-400/30 mx-auto mb-3" />
            <p className="text-gray-600 font-medium mb-2">{graph.title}</p>
            <p className="text-gray-500 text-sm">{message}</p>
          </div>
        </div>
      );
    }

    // Also check if chartData is completely empty
    if (!chartData || chartData.length === 0) {
      return (
        <div className="h-full flex items-center justify-center">
          <div className="text-center p-6">
            <Activity className="w-16 h-16 text-blue-400/30 mx-auto mb-3" />
            <p className="text-gray-600 font-medium mb-2">{graph.title}</p>
            <p className="text-gray-500 text-sm">No data available yet</p>
          </div>
        </div>
      );
    }

    // Convert Plotly figure to Chart.js format
    if (graph.chart_id === 'total_tokens_pie' && chartData[0]) {
      const labels = chartData[0].labels || [];
      const values = chartData[0].values || [];
      
      if (labels.length > 0 && values.length > 0) {
        const data = {
          labels,
          datasets: [{
            data: values,
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)',
              'rgba(16, 185, 129, 0.8)',
              'rgba(139, 92, 246, 0.8)',
              'rgba(251, 146, 60, 0.8)',
              'rgba(236, 72, 153, 0.8)',
            ],
            borderColor: 'rgba(255, 255, 255, 1)',
            borderWidth: 2,
          }]
        };
        return <Pie data={data} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />;
      }
    }

    if (graph.chart_id === 'tokens_per_call_bar' && chartData[0]) {
      const yLabels = chartData[0].y || []; // Names
      const xValues = chartData[0].x || []; // Values
      
      if (yLabels.length > 0 && xValues.length > 0) {
        const data = {
          labels: yLabels,
          datasets: [{
            label: 'Tokens per Call',
            data: xValues,
            backgroundColor: 'rgba(16, 185, 129, 0.8)',
            borderColor: 'rgba(16, 185, 129, 1)',
            borderWidth: 2,
          }]
        };
        return <Bar data={data} options={{ 
          indexAxis: 'y' as const,
          responsive: true, 
          maintainAspectRatio: false, 
          plugins: { legend: { display: false } } 
        }} />;
      }
    }

    if (graph.chart_id === 'efficiency_scatter' && chartData[0]) {
      const xValues = chartData[0].x || [];
      const yValues = chartData[0].y || [];
      const labels = chartData[0].text || [];
      
      if (xValues.length > 0 && yValues.length > 0) {
        const data = {
          datasets: [{
            label: 'Efficiency',
            data: xValues.map((x: number, i: number) => ({
              x,
              y: yValues[i] || 0
            })),
            backgroundColor: 'rgba(139, 92, 246, 0.8)',
            borderColor: 'rgba(139, 92, 246, 1)',
            borderWidth: 2,
            pointRadius: 8,
          }]
        };
        return <Scatter data={data} options={{ 
          responsive: true, 
          maintainAspectRatio: false,
          plugins: {
            tooltip: {
              callbacks: {
                label: (context: any) => {
                  const label = labels[context.dataIndex] || '';
                  return `${label}: (${context.parsed.x}, ${context.parsed.y})`;
                }
              }
            }
          }
        }} />;
      }
    }

    if ((graph.chart_id === 'recent_usage_timeline' || graph.chart_id === 'expiration_timeline') && chartData[0]) {
      const xValues = chartData[0].x || [];
      const yValues = chartData[0].y || [];
      
      if (xValues.length > 0 && yValues.length > 0) {
        // For timeline charts, x is dates and y is names
        const data = {
          labels: yValues,
          datasets: [{
            label: 'Activity',
            data: xValues.map((x: string) => new Date(x).getTime()),
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            pointRadius: 6,
            pointHoverRadius: 8,
          }]
        };
        return <Bar data={data} options={{ 
          indexAxis: 'y' as const,
          responsive: true, 
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context: any) => {
                  return new Date(context.parsed.x).toLocaleString();
                }
              }
            }
          }
        }} />;
      }
    }

    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center p-6">
          <BarChart3 className="w-16 h-16 text-gray-400/30 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">No data available</p>
          <p className="text-gray-500 text-sm mt-2">Start using the API to see analytics</p>
        </div>
      </div>
    );
  };

  if (authLoading || loadingGraphs) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-cyan-100 to-blue-200 flex items-center justify-center">
        <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-2xl p-8 border border-white/50">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-blue-600 font-medium">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 relative overflow-hidden">
      {/* Animated gradient mesh background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-gradient-to-br from-blue-400/30 to-cyan-400/30 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-400/30 to-pink-400/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-gradient-to-br from-cyan-400/30 to-teal-400/30 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-gradient-to-br from-indigo-400/30 to-blue-400/30 rounded-full blur-3xl animate-blob animation-delay-6000"></div>
        
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/40 rounded-full animate-float"></div>
        <div className="absolute top-1/3 right-1/3 w-3 h-3 bg-purple-400/40 rounded-full animate-float animation-delay-1000"></div>
        <div className="absolute bottom-1/3 left-1/2 w-2 h-2 bg-cyan-400/40 rounded-full animate-float animation-delay-2000"></div>
        <div className="absolute top-2/3 right-1/4 w-2 h-2 bg-pink-400/40 rounded-full animate-float animation-delay-3000"></div>
        
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808018_1px,transparent_1px),linear-gradient(to_bottom,#80808018_1px,transparent_1px)] bg-[size:64px_64px]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),rgba(255,255,255,0))]"></div>
      </div>

      {/* Header */}
      <div className="relative z-20 px-8 pt-6">
        <div className="max-w-7xl mx-auto backdrop-blur-xl bg-white/70 rounded-3xl shadow-2xl border border-white/60 px-8 py-6 hover:shadow-[0_20px_60px_-15px_rgba(59,130,246,0.3)] transition-all duration-500">
          <div className="flex justify-between items-center">
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300"
                >
                  <ArrowLeft className="w-6 h-6 text-white" />
                </button>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">Analytics Dashboard</h1>
                  <p className="text-blue-600/70 text-base font-light tracking-wide">Team usage and performance metrics</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowDebugInfo(!showDebugInfo)}
                  className="px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm"
                  title="Toggle debug info"
                >
                  Debug
                </button>
                <button
                  onClick={fetchGraphs}
                  disabled={loadingGraphs}
                  className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-400 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Refresh data"
                >
                  <RefreshCw className={`w-6 h-6 text-white ${loadingGraphs ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8 relative z-10">
        {/* Error Message */}
        {error && (
          <div className="mb-6 backdrop-blur-xl bg-red-50/80 border border-red-300/50 text-red-700 px-6 py-4 rounded-xl flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={fetchGraphs}
              className="ml-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Debug Info */}
        {showDebugInfo && (
          <div className="mb-6 backdrop-blur-xl bg-gray-50/80 border border-gray-300/50 text-gray-700 px-6 py-4 rounded-xl">
            <h3 className="font-bold mb-2">Debug Information</h3>
            <div className="space-y-2 text-sm">
              <p><strong>Graphs loaded:</strong> {graphs.length}</p>
              <p><strong>Loading:</strong> {loadingGraphs ? 'Yes' : 'No'}</p>
              <p><strong>Error:</strong> {error || 'None'}</p>
              <details className="mt-2">
                <summary className="cursor-pointer font-medium">Raw data</summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                  {JSON.stringify(graphs, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        )}

        {/* Charts Section - Dynamically Rendered */}
        {graphs.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-24 h-24 text-blue-400/30 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-700 mb-2">No Analytics Data Available</h2>
            <p className="text-gray-500 mb-4">
              The analytics dashboard will populate once your team starts using the API.
            </p>
            <button
              onClick={fetchGraphs}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh Data
            </button>
          </div>
        ) : (
          <>
            {/* First Row - 2 charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {graphs.slice(0, 2).map((graph, index) => {
                const colors = [
                  { from: 'blue-400', to: 'cyan-400', text: 'blue-900', subtext: 'blue-600/70', bg: 'blue-50/50 to-cyan-50/50' },
                  { from: 'emerald-400', to: 'teal-400', text: 'emerald-900', subtext: 'emerald-600/70', bg: 'emerald-50/50 to-teal-50/50' }
                ][index];

                return (
                  <div key={graph.chart_id} className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-xl p-6 border border-white/60 relative group">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h2 className={`text-2xl font-bold text-${colors.text} mb-1`}>{graph.title}</h2>
                        <p className={`text-${colors.subtext} text-sm`}>{graph.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setExpandedGraph(graph)}
                          className="p-2 hover:bg-blue-100/50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                          title="Expand"
                        >
                          <Maximize2 className="w-5 h-5 text-blue-600" />
                        </button>
                        <div className={`w-12 h-12 bg-gradient-to-br from-${colors.from} to-${colors.to} rounded-xl flex items-center justify-center shadow-lg`}>
                          <BarChart3 className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    </div>
                    <div className="h-64">
                      {renderChart(graph)}
                    </div>
                    <div className="mt-4 text-xs text-gray-500 text-center">
                      {graph.meta.records} records analyzed
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Second Row - Remaining 3 charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {graphs.slice(2).map((graph, index) => {
                const colors = [
                  { from: 'purple-400', to: 'pink-400', text: 'purple-900', subtext: 'purple-600/70', bg: 'purple-50/50 to-pink-50/50', icon: Activity },
                  { from: 'amber-400', to: 'orange-400', text: 'amber-900', subtext: 'amber-600/70', bg: 'amber-50/50 to-orange-50/50', icon: Calendar },
                  { from: 'indigo-400', to: 'blue-400', text: 'indigo-900', subtext: 'indigo-600/70', bg: 'indigo-50/50 to-blue-50/50', icon: Activity }
                ][index];

                const Icon = colors.icon;

                return (
                  <div key={graph.chart_id} className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-xl p-6 border border-white/60 relative group">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h2 className={`text-2xl font-bold text-${colors.text} mb-1`}>{graph.title}</h2>
                        <p className={`text-${colors.subtext} text-sm`}>{graph.description}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setExpandedGraph(graph)}
                          className="p-2 hover:bg-purple-100/50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                          title="Expand"
                        >
                          <Maximize2 className="w-5 h-5 text-purple-600" />
                        </button>
                        <div className={`w-12 h-12 bg-gradient-to-br from-${colors.from} to-${colors.to} rounded-xl flex items-center justify-center shadow-lg`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    </div>
                    <div className="h-80">
                      {renderChart(graph)}
                    </div>
                    <div className="mt-4 text-xs text-gray-500 text-center">
                      {graph.meta.records} records analyzed
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Expanded Graph Modal */}
      {expandedGraph && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-blue-200/50 px-8 py-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-blue-900">{expandedGraph.title}</h2>
                <p className="text-blue-600/70 text-sm mt-1">{expandedGraph.description}</p>
              </div>
              <button
                onClick={() => setExpandedGraph(null)}
                className="p-2 hover:bg-blue-100/50 rounded-lg transition-all duration-200"
                title="Close"
              >
                <X className="w-6 h-6 text-blue-600" />
              </button>
            </div>
            <div className="p-8">
              <div className="h-[600px]">
                {renderChart(expandedGraph)}
              </div>
              <div className="mt-6 text-center text-sm text-gray-500">
                {expandedGraph.meta.records} records analyzed
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}