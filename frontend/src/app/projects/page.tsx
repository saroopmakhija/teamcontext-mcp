'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { projectAPI } from '@/lib/api';
import { Project, ProjectCreate } from '@/types/project';
import { Plus, FolderOpen, Users, Trash2, Edit2, X, Loader2, ArrowLeft } from 'lucide-react';

export default function ProjectsPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: '',
    description: '',
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<{ id: string; name: string } | null>(null);

  useEffect(() => {
    // Wait for auth to finish loading before checking
    if (!authLoading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else {
        loadProjects();
      }
    }
  }, [isAuthenticated, authLoading, router]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await projectAPI.getProjects();
      setProjects(data);
    } catch (err: any) {
      console.error('Error loading projects:', err);
      setError(err.response?.data?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newProject.name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      setCreating(true);
      setError('');
      const created = await projectAPI.createProject(newProject);
      setProjects([...projects, created]);
      setShowCreateModal(false);
      setNewProject({ name: '', description: '' });
    } catch (err: any) {
      console.error('Error creating project:', err);
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteProject = async () => {
    if (!projectToDelete) return;

    try {
      await projectAPI.deleteProject(projectToDelete.id);
      setProjects(projects.filter(p => p.id !== projectToDelete.id));
      setShowDeleteModal(false);
      setProjectToDelete(null);
    } catch (err: any) {
      console.error('Error deleting project:', err);
      setError(err.response?.data?.detail || 'Failed to delete project');
      setShowDeleteModal(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-100 via-cyan-100 to-blue-200 flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-200/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="text-center relative z-10">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-blue-700 font-semibold">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 p-4 relative overflow-hidden">
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

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-2xl p-8 mb-6 border border-white/50">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="p-2 hover:bg-blue-100/50 rounded-xl transition-all duration-300 hover:scale-110 active:scale-95"
              >
                <ArrowLeft className="w-6 h-6 text-blue-600 hover:-translate-x-1 transition-transform" />
              </button>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">Your Projects</h1>
                <p className="text-blue-600/70 text-base font-light tracking-wide">Manage your team's context projects</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 shadow-lg shadow-blue-400/30 hover:shadow-2xl hover:shadow-blue-400/50 transform hover:-translate-y-1 hover:scale-105 active:scale-95"
            >
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
              New Project
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="backdrop-blur-xl bg-red-50/80 border border-red-300/50 text-red-700 px-4 py-3 rounded-xl mb-6">
            {error}
          </div>
        )}

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-2xl p-12 text-center border border-white/50">
            <FolderOpen className="w-16 h-16 text-blue-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-blue-800 mb-2">No Projects Yet</h3>
            <p className="text-blue-600/70 mb-6">Create your first project to get started</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-blue-400 to-cyan-400 hover:from-blue-500 hover:to-cyan-500 text-white px-8 py-3 rounded-xl font-semibold transition-all shadow-lg shadow-blue-400/30 hover:shadow-xl hover:shadow-blue-400/40 transform hover:-translate-y-0.5"
            >
              <Plus className="w-5 h-5 inline mr-2" />
              Create Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => router.push(`/projects/${project.id}`)}
                className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-2 hover:scale-[1.02] active:scale-[0.98] group cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-all duration-300">
                    <FolderOpen className="w-6 h-6 text-white" />
                  </div>
                  {user?.id === project.owner_id && (
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          alert('Edit feature coming soon!');
                        }}
                        className="p-2 hover:bg-blue-100/50 rounded-lg transition-all duration-200 hover:scale-110 active:scale-95"
                      >
                        <Edit2 className="w-4 h-4 text-blue-600" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setProjectToDelete({ id: project.id, name: project.name });
                          setShowDeleteModal(true);
                        }}
                        className="p-2 hover:bg-red-100/50 rounded-lg transition-all duration-200 hover:scale-110 active:scale-95"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  )}
                </div>
                
                <h3 className="text-xl font-bold text-blue-900 mb-2">{project.name}</h3>
                <p className="text-blue-600/70 text-sm mb-4 line-clamp-2">{project.description}</p>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-blue-500" />
                    <span className="text-blue-700 font-medium">{project.contributors.length + 1} members</span>
                  </div>
                  <span className="text-blue-600/60">by {project.owner_name}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Project Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="backdrop-blur-xl bg-white/90 rounded-3xl shadow-2xl p-8 max-w-md w-full border border-white/50">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Create New Project</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-blue-100/50 rounded-xl transition-colors"
                >
                  <X className="w-6 h-6 text-blue-600" />
                </button>
              </div>

              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-semibold text-blue-700 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/50 backdrop-blur-sm border border-blue-200/50 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent focus:bg-white/80 transition-all text-blue-900 placeholder:text-blue-400/50"
                    placeholder="Enter project name"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-semibold text-blue-700 mb-2">
                    Description
                  </label>
                  <textarea
                    id="description"
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="w-full px-4 py-3 bg-white/50 backdrop-blur-sm border border-blue-200/50 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent focus:bg-white/80 transition-all text-blue-900 placeholder:text-blue-400/50 min-h-[100px]"
                    placeholder="Describe your project"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={creating}
                  className="w-full bg-gradient-to-r from-blue-400 to-cyan-400 text-white py-4 px-4 rounded-xl font-semibold hover:from-blue-500 hover:to-cyan-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-400/30 hover:shadow-xl hover:shadow-blue-400/40 transform hover:-translate-y-0.5"
                >
                  {creating ? (
                    <div className="flex items-center justify-center">
                      <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      Creating...
                    </div>
                  ) : (
                    'Create Project'
                  )}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && projectToDelete && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="backdrop-blur-xl bg-white/90 rounded-3xl shadow-2xl p-8 max-w-md w-full border border-white/50 transform transition-all duration-300 scale-100">
              <div className="text-center mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-red-400 to-pink-400 rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl animate-pulse">
                  <Trash2 className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  Delete Project?
                </h2>
                <p className="text-gray-600 text-sm">
                  This action cannot be undone
                </p>
              </div>

              <div className="backdrop-blur-sm bg-red-50/80 rounded-2xl p-4 mb-6 border border-red-200/50">
                <p className="text-gray-700 text-sm mb-2">
                  You are about to delete:
                </p>
                <p className="font-bold text-gray-900 text-lg">
                  {projectToDelete.name}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setProjectToDelete(null);
                  }}
                  className="flex-1 bg-white border border-gray-300 text-gray-700 py-3 px-4 rounded-xl font-semibold hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 hover:scale-105 active:scale-95"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteProject}
                  className="flex-1 bg-gradient-to-r from-red-400 to-pink-400 text-white py-3 px-4 rounded-xl font-semibold hover:from-red-500 hover:to-pink-500 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200 shadow-lg shadow-red-400/30 hover:shadow-xl hover:shadow-red-400/40 transform hover:-translate-y-0.5 hover:scale-105 active:scale-95"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
