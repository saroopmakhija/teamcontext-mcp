'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { projectAPI, contextAPI } from '@/lib/api';
import { Project } from '@/types/project';
import { APP_CONFIG } from '@/config/constants';
import KnowledgeGraph from '@/components/KnowledgeGraph';
import {
  ArrowLeft,
  Users,
  Search,
  UserPlus,
  X,
  Loader2,
  FileText,
  Trash2,
  Upload,
  Plus
} from 'lucide-react';

interface SearchResult {
  id: string;
  content: string;
  similarity_score: number;
  metadata: {
    source?: string;
    tags?: string[];
    project_id?: string;
    created_by?: string;
  };
  created_at: string;
}

export default function ProjectDetailPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Context search states (Chat UI)
  const [searchQuery, setSearchQuery] = useState('');
  const [messages, setMessages] = useState<Array<{
    id: string;
    type: 'user' | 'bot';
    content: string;
    results?: SearchResult[];
    timestamp: Date;
  }>>([]);
  const [searching, setSearching] = useState(false);
  
  // Add contributor states
  const [showAddContributor, setShowAddContributor] = useState(false);
  const [contributorEmail, setContributorEmail] = useState('');
  const [addingContributor, setAddingContributor] = useState(false);

  // Add context states
  const [showAddContext, setShowAddContext] = useState(false);
  const [contextText, setContextText] = useState('');
  const [contextFiles, setContextFiles] = useState<File[]>([]);
  const [uploadingContext, setUploadingContext] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && isAuthenticated && projectId) {
      loadProject();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, projectId, router]);

  const loadProject = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await projectAPI.getProject(projectId);
      setProject(data);
    } catch (err) {
      console.error('Error loading project:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    const userQuery = searchQuery;
    const userMessageId = Date.now().toString();

    // Add user message
    setMessages(prev => [...prev, {
      id: userMessageId,
      type: 'user',
      content: userQuery,
      timestamp: new Date()
    }]);

    setSearchQuery(''); // Clear input
    setSearching(true);

    try {
      const results = await contextAPI.search(
        userQuery, 
        projectId as string, 
        APP_CONFIG.search.similarityThreshold, 
        APP_CONFIG.search.defaultLimit
      );

      // Add bot response
      const botMessage = results.length > 0
        ? `Found ${results.length} relevant result${results.length !== 1 ? 's' : ''} for "${userQuery}"`
        : `No results found for "${userQuery}". Try a different query.`;

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: botMessage,
        results: results,
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('Search error:', err);
      
      // Add error message as bot response
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `Sorry, I couldn't search for that. Please try again.`,
        timestamp: new Date()
      }]);
    } finally {
      setSearching(false);
    }
  };

  const handleAddContributor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!contributorEmail.trim()) return;

    try {
      setAddingContributor(true);
      setError('');
      await projectAPI.addContributor(projectId, { email: contributorEmail });
      setContributorEmail('');
      setShowAddContributor(false);
      await loadProject(); // Reload to show new contributor
    } catch (err) {
      console.error('Error adding contributor:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to add contributor');
    } finally {
      setAddingContributor(false);
    }
  };

  const handleRemoveContributor = async (userId: string) => {
    if (!confirm(APP_CONFIG.messages.confirmRemoveContributor)) return;

    try {
      await projectAPI.removeContributor(projectId, userId);
      await loadProject(); // Reload to update contributor list
    } catch (err) {
      console.error('Error removing contributor:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to remove contributor');
    }
  };

  const handleAddContext = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!contextText.trim() && contextFiles.length === 0) {
      setError('Please enter text or upload files');
      return;
    }

    try {
      setUploadingContext(true);
      setError('');

      let successCount = 0;

      // Save text content
      if (contextText.trim()) {
        await contextAPI.save(
          contextText,
          'user_input',
          projectId,
          ['user-uploaded', 'text']
        );
        successCount++;
      }

      // Save each file
      for (const file of contextFiles) {
        const content = await file.text();
        await contextAPI.save(
          content,
          'file_upload',
          projectId,
          ['user-uploaded', 'file', file.name]
        );
        successCount++;
      }

      // Reset form
      setContextText('');
      setContextFiles([]);
      setShowAddContext(false);

      // Show success message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'bot',
        content: `✅ Successfully added ${successCount} item${successCount !== 1 ? 's' : ''} to project context! Auto-linked to similar chunks.`,
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('Error adding context:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to add context');
    } finally {
      setUploadingContext(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    setContextFiles(prev => [...prev, ...files]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setContextFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setContextFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 flex items-center justify-center">
        <div className="backdrop-blur-xl bg-white/70 rounded-3xl shadow-2xl p-8 border border-white/60">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-blue-600 font-medium">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 flex items-center justify-center p-4">
        <div className="backdrop-blur-xl bg-white/70 rounded-3xl shadow-2xl p-8 border border-white/60 text-center">
          <p className="text-red-600 font-medium mb-4">{error || 'Project not found'}</p>
          <button
            onClick={() => router.push('/projects')}
            className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  const isOwner = project.owner_id === user?.id;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 relative overflow-hidden">
      {/* Animated gradient mesh background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Large animated orbs */}
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-gradient-to-br from-blue-400/30 to-cyan-400/30 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-400/30 to-pink-400/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-gradient-to-br from-cyan-400/30 to-teal-400/30 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-gradient-to-br from-indigo-400/30 to-blue-400/30 rounded-full blur-3xl animate-blob animation-delay-6000"></div>
        
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/40 rounded-full animate-float"></div>
        <div className="absolute top-1/3 right-1/3 w-3 h-3 bg-purple-400/40 rounded-full animate-float animation-delay-1000"></div>
        <div className="absolute bottom-1/3 left-1/2 w-2 h-2 bg-cyan-400/40 rounded-full animate-float animation-delay-2000"></div>
        <div className="absolute top-2/3 right-1/4 w-2 h-2 bg-pink-400/40 rounded-full animate-float animation-delay-3000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-teal-400/40 rounded-full animate-float animation-delay-4000"></div>
        
        {/* Grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808018_1px,transparent_1px),linear-gradient(to_bottom,#80808018_1px,transparent_1px)] bg-[size:64px_64px]"></div>
        
        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),rgba(255,255,255,0))]"></div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8 relative z-10">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/70 rounded-3xl shadow-lg p-6 mb-6 border border-white/60 hover:shadow-[0_20px_60px_-15px_rgba(59,130,246,0.3)] transition-all duration-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/projects')}
                className="p-2 hover:bg-blue-100/50 rounded-xl transition-colors"
              >
                <ArrowLeft className="w-6 h-6 text-blue-600" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-blue-900">{project.name}</h1>
                <p className="text-sm text-blue-600/70">
                  Owner: {project.owner_name} • Created {formatDate(project.created_at)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-blue-600/70">
              <Users className="w-4 h-4" />
              <span>{(project.contributors?.length || 0) + 1} members</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="backdrop-blur-xl bg-red-50/80 border border-red-300/50 text-red-700 px-4 py-3 rounded-xl mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Project Info & Contributors */}
          <div className="lg:col-span-1 space-y-6">
            {/* Description */}
            <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-1">
              <h2 className="text-xl font-bold text-blue-900 mb-3">Description</h2>
              <p className="text-blue-700 leading-relaxed">
                {project.description || 'No description provided'}
              </p>
            </div>

            {/* Contributors */}
            <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-1">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-blue-900">Contributors</h2>
                {isOwner && (
                  <button
                    onClick={() => setShowAddContributor(!showAddContributor)}
                    className="p-2 hover:bg-blue-100/50 rounded-lg transition-colors"
                  >
                    {showAddContributor ? <X className="w-5 h-5 text-blue-600" /> : <UserPlus className="w-5 h-5 text-blue-600" />}
                  </button>
                )}
              </div>

              {/* Add Contributor Form */}
              {showAddContributor && (
                <form onSubmit={handleAddContributor} className="mb-4">
                  <input
                    type="email"
                    value={contributorEmail}
                    onChange={(e) => setContributorEmail(e.target.value)}
                    placeholder="Enter email address"
                    className="w-full px-4 py-2 rounded-xl border border-blue-200/50 bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-400 mb-2 text-black font-medium placeholder:text-gray-400"
                    required
                  />
                  <button
                    type="submit"
                    disabled={addingContributor}
                    className="w-full bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-4 py-2 rounded-xl font-semibold transition-all shadow-lg disabled:opacity-50"
                  >
                    {addingContributor ? 'Adding...' : 'Add Contributor'}
                  </button>
                </form>
              )}

              {/* Owner */}
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-blue-900">{project.owner_name}</p>
                      <p className="text-xs text-blue-600/70">Owner</p>
                    </div>
                  </div>
                </div>

                {/* Contributors List */}
                {project.contributors?.map((contributor: { id: string; name: string; email: string }) => (
                  <div key={contributor.id} className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-teal-400 rounded-full flex items-center justify-center">
                        <Users className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="font-bold text-black">{contributor.name}</p>
                        <p className="text-xs text-gray-800 font-medium">{contributor.email}</p>
                      </div>
                    </div>
                    {isOwner && (
                      <button
                        onClick={() => handleRemoveContributor(contributor.id)}
                        className="p-1 hover:bg-red-100/50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Add Context Section */}
            <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-1">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-blue-900">Add Context</h2>
                <button
                  onClick={() => setShowAddContext(!showAddContext)}
                  className="p-2 hover:bg-blue-100/50 rounded-lg transition-colors"
                >
                  {showAddContext ? <X className="w-5 h-5 text-blue-600" /> : <Plus className="w-5 h-5 text-blue-600" />}
                </button>
              </div>

              {showAddContext && (
                <form onSubmit={handleAddContext} className="space-y-4">
                  {/* Text Input */}
                  <div>
                    <label className="block text-sm font-semibold text-blue-900 mb-2">
                      Paste Text or Code
                    </label>
                    <textarea
                      value={contextText}
                      onChange={(e) => setContextText(e.target.value)}
                      placeholder="Paste your code, documentation, or any text here..."
                      className="w-full px-4 py-3 rounded-xl border border-blue-200/50 bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-400 min-h-[120px] text-black font-mono text-sm placeholder:text-gray-400 resize-y"
                    />
                  </div>

                  {/* File Upload - Drag & Drop */}
                  <div>
                    <label className="block text-sm font-semibold text-blue-900 mb-2">
                      Upload Files
                    </label>
                    <div
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      className={`border-2 border-dashed rounded-xl p-6 text-center transition-all ${
                        isDragging
                          ? 'border-blue-500 bg-blue-50/50'
                          : 'border-blue-200/50 bg-white/50'
                      }`}
                    >
                      <Upload className={`w-8 h-8 mx-auto mb-2 ${isDragging ? 'text-blue-500' : 'text-blue-400'}`} />
                      <p className="text-sm font-medium text-blue-900 mb-1">
                        Drag & drop files here
                      </p>
                      <p className="text-xs text-blue-600/70 mb-3">
                        or click to browse
                      </p>
                      <input
                        type="file"
                        multiple
                        onChange={handleFileSelect}
                        className="hidden"
                        id="file-upload"
                        accept=".txt,.md,.py,.js,.jsx,.ts,.tsx,.json,.html,.css,.java,.cpp,.c,.go,.rs,.rb,.php,.swift,.kt"
                      />
                      <label
                        htmlFor="file-upload"
                        className="inline-block bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-4 py-2 rounded-lg font-semibold text-sm cursor-pointer transition-all shadow-md"
                      >
                        Browse Files
                      </label>
                    </div>

                    {/* Selected Files List */}
                    {contextFiles.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {contextFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-blue-50/50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <FileText className="w-4 h-4 text-blue-600" />
                              <span className="text-sm text-blue-900 font-medium">{file.name}</span>
                              <span className="text-xs text-blue-600/70">
                                ({(file.size / 1024).toFixed(1)} KB)
                              </span>
                            </div>
                            <button
                              type="button"
                              onClick={() => removeFile(index)}
                              className="p-1 hover:bg-red-100/50 rounded transition-colors"
                            >
                              <X className="w-4 h-4 text-red-600" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={uploadingContext || (!contextText.trim() && contextFiles.length === 0)}
                    className="w-full bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-4 py-3 rounded-xl font-semibold transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {uploadingContext ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Add to Context
                      </>
                    )}
                  </button>
                </form>
              )}

              {!showAddContext && (
                <p className="text-sm text-blue-600/70">
                  Click the + button to add text or files to your project context
                </p>
              )}
            </div>
          </div>

          {/* Right Column - Context Chat */}
          <div className="lg:col-span-2">
            <div className="backdrop-blur-xl bg-gradient-to-br from-emerald-50/80 to-teal-50/80 rounded-2xl shadow-xl border border-emerald-200/50 flex flex-col" style={{ height: APP_CONFIG.ui.chatHeight }}>
              <div className="p-6 border-b border-emerald-200/50">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 via-teal-400 to-green-400 bg-clip-text text-transparent" style={{ textShadow: '0 0 40px rgba(16, 185, 129, 0.5), 0 0 20px rgba(20, 184, 166, 0.3)' }}>
                  Context Chat
                </h2>
                <p className="text-base font-semibold bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent mt-1" style={{ textShadow: '0 0 30px rgba(16, 185, 129, 0.4)' }}>
                  Ask questions about your project
                </p>
              </div>
              
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center max-w-2xl">
                      <h3 className="text-5xl font-bold bg-gradient-to-r from-emerald-400 via-teal-400 to-green-400 bg-clip-text text-transparent mb-4" style={{ textShadow: '0 0 40px rgba(16, 185, 129, 0.5), 0 0 20px rgba(20, 184, 166, 0.3)' }}>
                        Hi, {user?.name ? user.name.charAt(0).toUpperCase() + user.name.slice(1).toLowerCase() : 'there'}!
                      </h3>
                      <p className="text-2xl font-semibold bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent" style={{ textShadow: '0 0 30px rgba(16, 185, 129, 0.4)' }}>
                        How can I help you today?
                      </p>
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                        {/* Message Bubble */}
                        <div className={`rounded-2xl p-4 ${
                          message.type === 'user'
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                            : 'bg-white/90 backdrop-blur-sm border border-emerald-200/50 text-gray-900'
                        } shadow-lg`}>
                          <p className="text-sm font-medium">{message.content}</p>
                          <p className="text-xs mt-1 opacity-70">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>

                        {/* Bot Results */}
                        {message.type === 'bot' && message.results && message.results.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {message.results.map((result) => (
                              <div
                                key={result.id}
                                className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-emerald-200/30 hover:shadow-lg transition-shadow"
                              >
                                <div className="flex items-start gap-3">
                                  <FileText className="w-5 h-5 text-emerald-600 mt-1 flex-shrink-0" />
                                  <div className="flex-1">
                                    <p className="text-sm text-gray-800 mb-2">{result.content}</p>
                                    <div className="flex items-center gap-3 text-xs text-gray-600">
                                      <span className="font-semibold text-emerald-600">
                                        {(result.similarity_score * 100).toFixed(0)}% match
                                      </span>
                                      {result.metadata.source && (
                                        <span>• {result.metadata.source}</span>
                                      )}
                                    </div>
                                    {result.metadata.tags && result.metadata.tags.length > 0 && (
                                      <div className="flex gap-2 mt-2 flex-wrap">
                                        {result.metadata.tags.map((tag, idx) => (
                                          <span
                                            key={idx}
                                            className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-lg"
                                          >
                                            {tag}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {/* Typing Indicator */}
                {searching && (
                  <div className="flex justify-start">
                    <div className="bg-white/90 backdrop-blur-sm border border-emerald-200/50 rounded-2xl p-4 shadow-lg">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce animation-delay-200"></div>
                          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce animation-delay-400"></div>
                        </div>
                        <span className="text-xs text-gray-600">Searching...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Form */}
              <form onSubmit={handleSearch} className="p-4 border-t border-emerald-200/50">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Ask about project context..."
                    className="flex-1 px-4 py-3 rounded-xl border border-emerald-200/50 bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 text-black font-medium placeholder:text-gray-400"
                    disabled={searching}
                  />
                  <button
                    type="submit"
                    disabled={searching || !searchQuery.trim()}
                    className="bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-500 hover:to-teal-500 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
                  >
                    <Search className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Separator Line */}
        <div className="my-8">
          <div className="h-px bg-gradient-to-r from-transparent via-blue-200/50 to-transparent"></div>
        </div>

        {/* Knowledge Graph Section */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-8 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Knowledge Graph</h2>
              <p className="text-sm text-gray-600">Interactive visualization of project knowledge connections</p>
            </div>
          </div>

          {/* Graph Container */}
          <KnowledgeGraph projectId={projectId} />
        </div>
      </div>
    </div>
  );
}

