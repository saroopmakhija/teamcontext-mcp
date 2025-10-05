'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { projectAPI } from '@/lib/api';
import { Project } from '@/types/project';
import { LogOut, User, Mail, Key, Loader2, ChevronDown, FolderOpen, Users, Clock, Info, Search, BookOpen, Zap, Shield } from 'lucide-react';

export default function DashboardPage() {
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [showDropdown, setShowDropdown] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  useEffect(() => {
    // Wait for auth to finish loading before checking
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated, authLoading, router]);

  const loadProjects = async () => {
    try {
      setLoadingProjects(true);
      const data = await projectAPI.getProjects();
      setProjects(data);
    } catch (err) {
      console.error('Error loading projects:', err);
    } finally {
      setLoadingProjects(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays} days ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Show loading while auth is being checked
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-cyan-100 to-blue-200 flex items-center justify-center">
        <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-2xl p-8 border border-white/50">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-blue-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // If not authenticated after loading, don't render anything (will redirect)
  if (!isAuthenticated) {
    return null;
  }

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
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:64px_64px]"></div>
        
        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),rgba(255,255,255,0))]"></div>
      </div>

      {/* Navbar with rounded edges */}
      <div className="relative z-20 px-8 pt-6">
        <div className="max-w-7xl mx-auto backdrop-blur-xl bg-white/70 rounded-3xl shadow-2xl border border-white/60 px-8 py-6 hover:shadow-[0_20px_60px_-15px_rgba(59,130,246,0.3)] transition-all duration-500">
          <div className="flex justify-between items-center">
            <div className="flex-1">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">Welcome to TeamContext!</h1>
              <p className="text-blue-600/70 text-base font-light tracking-wide">Manage your team's context and knowledge sharing</p>
            </div>

            {/* About Link */}
            <button
              onClick={() => router.push('/about')}
              className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-6 py-2.5 rounded-xl font-semibold transition-all duration-300 shadow-lg shadow-blue-400/30 hover:shadow-2xl hover:shadow-blue-400/50 transform hover:-translate-y-1 hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <Info className="w-5 h-5" />
              About Us
            </button>
            
            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="flex items-center gap-3 hover:bg-blue-100/50 rounded-2xl px-4 py-2 transition-all duration-300 hover:scale-105 active:scale-95"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300">
                  <User className="w-6 h-6 text-white" />
                </div>
                <ChevronDown className={`w-5 h-5 text-blue-600 transition-transform duration-300 ${showDropdown ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown Menu */}
              {showDropdown && (
                <div className="absolute right-0 mt-2 w-80 backdrop-blur-xl bg-white/90 rounded-2xl shadow-2xl border border-white/50 overflow-hidden">
                  {/* User Info Header */}
                  <div className="bg-gradient-to-br from-blue-50/80 to-cyan-50/80 p-4 border-b border-blue-200/30">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-full flex items-center justify-center shadow-lg">
                        <User className="w-7 h-7 text-white" />
                      </div>
                      <div>
                        <p className="font-bold text-blue-900 text-lg">{user?.name || 'User'}</p>
                        <p className="text-sm text-blue-600/70">{user?.email}</p>
                      </div>
                    </div>
                  </div>

                  {/* Account Details */}
                  <div className="p-4">
                    <h3 className="text-sm font-bold text-blue-700 mb-3">Account Information</h3>
                    
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center gap-3 bg-blue-50/50 p-3 rounded-xl">
                        <Mail className="w-4 h-4 text-blue-600" />
                        <div className="flex-1">
                          <p className="text-xs text-blue-600/70 font-medium">Email</p>
                          <p className="text-sm font-semibold text-blue-900">{user?.email || 'N/A'}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 bg-blue-50/50 p-3 rounded-xl">
                        <User className="w-4 h-4 text-blue-600" />
                        <div className="flex-1">
                          <p className="text-xs text-blue-600/70 font-medium">Name</p>
                          <p className="text-sm font-semibold text-blue-900">{user?.name || 'N/A'}</p>
                        </div>
                      </div>

                      {user?.apiKey && (
                        <div className="bg-amber-50/80 p-3 rounded-xl border border-amber-300/50">
                          <div className="flex items-center gap-2 mb-2">
                            <Key className="w-4 h-4 text-amber-600" />
                            <p className="text-xs font-bold text-amber-800">API Key</p>
                          </div>
                          <p className="text-xs text-amber-700 mb-2">⚠️ Save securely</p>
                          <div className="bg-amber-100/80 p-2 rounded-lg font-mono text-xs text-amber-900 break-all">
                            {user.apiKey}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Logout Button */}
                    <button
                      onClick={handleLogout}
                      className="w-full bg-gradient-to-r from-red-400 to-pink-400 hover:from-red-500 hover:to-pink-500 text-white px-4 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg shadow-red-400/30 hover:shadow-2xl hover:shadow-red-400/50 transform hover:scale-105 active:scale-95"
                    >
                      <LogOut className="w-5 h-5" />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8 relative z-10">
        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Features */}
          <div className="lg:col-span-1 space-y-6">
            {/* API Access Card */}
            <div 
              onClick={() => router.push('/api-access')}
              className="backdrop-blur-xl bg-white/60 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300 border border-white/50 hover:-translate-y-2 hover:scale-[1.02] active:scale-[0.98] group cursor-pointer"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-400 rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-all duration-300">
                <Key className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-purple-800 mb-2">API Access</h3>
              <p className="text-purple-600/70 text-sm mb-4 font-medium leading-relaxed">
                Use your API key to integrate D-RAG with your development workflow.
              </p>
              <div className="bg-gradient-to-r from-purple-100/80 to-pink-100/80 backdrop-blur-sm text-purple-700 px-4 py-2 rounded-xl text-xs font-bold inline-block border border-purple-300/50">
                Manage Keys
              </div>
            </div>

            {/* Quick Actions */}
            <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/projects')}
                  className="w-full flex items-center gap-3 p-3 bg-blue-50/50 hover:bg-blue-100/50 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 text-left"
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center">
                    <FolderOpen className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">Create Project</p>
                    <p className="text-xs text-gray-600">Start a new project</p>
                  </div>
                </button>
                <button
                  onClick={() => router.push('/about')}
                  className="w-full flex items-center gap-3 p-3 bg-orange-50/50 hover:bg-orange-100/50 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 text-left"
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-red-400 rounded-lg flex items-center justify-center">
                    <Info className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">Learn More</p>
                    <p className="text-xs text-gray-600">About D-RAG</p>
                  </div>
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <FolderOpen className="w-5 h-5 text-blue-600" />
                    <span className="text-sm font-medium text-gray-700">Total Projects</span>
                  </div>
                  <span className="text-lg font-bold text-blue-600">{projects.length}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-emerald-50/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Users className="w-5 h-5 text-emerald-600" />
                    <span className="text-sm font-medium text-gray-700">Collaborators</span>
                  </div>
                  <span className="text-lg font-bold text-emerald-600">
                    {projects.reduce((acc, p) => acc + (p.contributors?.length || 0), 0) + projects.length}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Key className="w-5 h-5 text-purple-600" />
                    <span className="text-sm font-medium text-gray-700">API Status</span>
                  </div>
                  <span className="text-sm font-bold text-emerald-600">Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Projects Section */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-1">Your Projects</h2>
                <p className="text-blue-600/70 text-sm font-light tracking-wide">Recent projects you're working on</p>
              </div>
              <button
                onClick={() => router.push('/projects')}
                className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-5 py-2.5 rounded-xl font-semibold transition-all duration-300 shadow-lg shadow-blue-400/30 hover:shadow-2xl hover:shadow-blue-400/50 transform hover:-translate-y-1 hover:scale-105 active:scale-95 text-sm"
              >
                View All Projects
              </button>
            </div>

            {loadingProjects ? (
              <div className="backdrop-blur-xl bg-white/60 rounded-2xl shadow-xl p-12 border border-white/50 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-600" />
                <p className="text-blue-600/70 font-medium">Loading projects...</p>
              </div>
            ) : projects.length === 0 ? (
              <div className="backdrop-blur-xl bg-white/60 rounded-2xl shadow-xl p-12 border border-white/50 text-center">
                <FolderOpen className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                <h3 className="text-xl font-bold text-blue-800 mb-2">No projects yet</h3>
                <p className="text-blue-600/70 mb-6">Create your first project to get started</p>
                <button
                  onClick={() => router.push('/projects')}
                  className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg"
                >
                  Create Project
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {projects.slice(0, 6).map((project) => (
                <button
                  key={project.id}
                  onClick={() => router.push(`/projects/${project.id}`)}
                  className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-5 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 border border-white/60 hover:-translate-y-2 hover:scale-[1.02] active:scale-[0.98] text-left group"
                >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center shadow-md group-hover:scale-110 transition-all duration-300">
                          <FolderOpen className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-blue-900 truncate text-base">{project.name}</h3>
                        </div>
                      </div>
                    </div>

                    {project.description && (
                      <p className="text-blue-600/70 text-sm mb-3 line-clamp-2">{project.description}</p>
                    )}

                    <div className="flex items-center justify-between text-xs text-blue-600/60">
                      <div className="flex items-center gap-1">
                        <Users className="w-3.5 h-3.5" />
                        <span>{project.contributors?.length || 1} contributor{(project.contributors?.length || 1) !== 1 ? 's' : ''}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{formatDate(project.updated_at || project.created_at)}</span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
