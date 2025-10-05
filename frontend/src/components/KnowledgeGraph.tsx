'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import dynamic from 'next/dynamic';
import { Loader2, ZoomIn, ZoomOut, Locate, Move, RotateCw, MousePointer2, Hand } from 'lucide-react';
import * as THREE from 'three';

// Dynamically import ForceGraph3D to avoid SSR issues
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ height: '500px' }}>
      <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
    </div>
  ),
});

interface GraphNode {
  id: string;
  content: string;
  tags: string[]; // Adjacency list - linked chunk IDs
  name?: string;
  color?: string;
  metadata?: {
    source?: string;
    created_by?: string;
    chunk_index?: number;
  };
}

interface GraphLink {
  source: string;
  target: string;
}

interface ChunkDetails {
  chunk_id: string;
  content: string;
  tags: string[];
  metadata: any;
  created_at: string;
  accessed_count: number;
}

interface KnowledgeGraphProps {
  projectId: string;
}

export default function KnowledgeGraph({ projectId }: KnowledgeGraphProps) {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [chunkDetails, setChunkDetails] = useState<ChunkDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hoveredLink, setHoveredLink] = useState<any>(null);
  const fgRef = useRef<any>();

  useEffect(() => {
    loadGraphData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch all chunks using search with empty/wildcard query
      const accessToken = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/context/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          query: ' ', // Space to get all chunks
          project_id: projectId,
          similarity_threshold: 0.0, // Get everything
          limit: 1000
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch graph data');
      }

      const data = await response.json();
      
      // Create nodes with initial positions centered at origin
      const numNodes = data.length;
      
      const nodes: GraphNode[] = data.map((item: any, index: number) => {
        // Use spherical distribution for better 3D centering
        const phi = Math.acos(-1 + (2 * index) / numNodes);
        const theta = Math.sqrt(numNodes * Math.PI) * phi;
        const radius = 150; // Much larger radius for better visibility
        
        return {
          id: item.id,
          content: item.content,
          tags: item.metadata?.tags || [],
          name: item.content.substring(0, 30) + '...',
          x: radius * Math.cos(theta) * Math.sin(phi),
          y: radius * Math.sin(theta) * Math.sin(phi),
          z: radius * Math.cos(phi),
          metadata: {
            source: item.metadata?.source,
            created_by: item.metadata?.created_by,
            chunk_index: item.metadata?.chunk_index
          }
        };
      });

      // Create links from adjacency lists
      const links: GraphLink[] = [];
      nodes.forEach(node => {
        node.tags.forEach(targetId => {
          // Only add link if target node exists
          if (nodes.find(n => n.id === targetId)) {
            links.push({
              source: node.id,
              target: targetId
            });
          }
        });
      });

      setGraphData({ nodes, links });
      setLoading(false);
      
      // Position camera IMMEDIATELY at the perfect location - no delay, no transition
      setTimeout(() => {
        if (fgRef.current) {
          // Set camera to exact position instantly - matching the target view
          fgRef.current.cameraPosition(
            { x: 0, y: 0, z: 450 }, // Camera at optimal distance for 150 radius graph
            { x: 0, y: 0, z: 0 },   // Look at origin (center)
            0 // INSTANT - no transition animation
          );
          
          // Configure controls for both panning and rotation
          const controls = fgRef.current.controls();
          if (controls) {
            controls.target.set(0, 0, 0);
            controls.enablePan = true;
            controls.enableRotate = true;
            controls.enableZoom = true;
            controls.screenSpacePanning = true;
            
            // Reduce sensitivity for smooth control
            controls.panSpeed = 0.4; // Smooth panning
            controls.rotateSpeed = 0.6; // Smooth rotation
            controls.zoomSpeed = 0.6; // Smooth zoom
            
            // Default to rotate mode (empty space)
            controls.mouseButtons = {
              LEFT: 0,   // Rotate with left button
              MIDDLE: 1, // Zoom with middle button
              RIGHT: 2   // Pan with right button
            };
            
            controls.update();
          }
        }
      }, 100);
    } catch (err) {
      console.error('Error loading graph:', err);
      setError('Failed to load knowledge graph');
      setLoading(false);
    }
  };

  const fetchChunkDetails = async (chunkId: string) => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/context/${chunkId}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch chunk details');
      }

      const data = await response.json();
      setChunkDetails(data);
    } catch (err) {
      console.error('Error fetching chunk details:', err);
    }
  };

  const handleNodeHover = useCallback((node: GraphNode | null) => {
    setHoveredNode(node);
    if (node) {
      fetchChunkDetails(node.id);
    } else {
      setChunkDetails(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleNodeClick = useCallback((node: GraphNode) => {
    // Focus camera on node
    if (fgRef.current) {
      const distance = 200;
      const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);

      fgRef.current.cameraPosition(
        {
          x: (node.x || 0) * distRatio,
          y: (node.y || 0) * distRatio,
          z: (node.z || 0) * distRatio
        },
        node,
        1000
      );
    }
  }, []);

  const handleLinkHover = useCallback((link: any) => {
    setHoveredLink(link);
    
    // When hovering over a link, configure controls for panning
    if (fgRef.current) {
      const controls = fgRef.current.controls();
      if (controls && link) {
        // Pan mode when over link
        controls.mouseButtons = {
          LEFT: 2,   // Pan with left button
          MIDDLE: 1, // Zoom with middle button
          RIGHT: 0   // Rotate with right button
        };
      } else if (controls && !link) {
        // Rotate mode when not over link (empty space)
        controls.mouseButtons = {
          LEFT: 0,   // Rotate with left button
          MIDDLE: 1, // Zoom with middle button
          RIGHT: 2   // Pan with right button
        };
      }
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    if (fgRef.current) {
      const camera = fgRef.current.camera();
      const currentPos = camera.position;
      const factor = 0.8; // Zoom in by 20%
      
      fgRef.current.cameraPosition(
        {
          x: currentPos.x * factor,
          y: currentPos.y * factor,
          z: currentPos.z * factor
        },
        { x: 0, y: 0, z: 0 }, // Always look at center
        500
      );
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (fgRef.current) {
      const camera = fgRef.current.camera();
      const currentPos = camera.position;
      const factor = 1.2; // Zoom out by 20%
      
      fgRef.current.cameraPosition(
        {
          x: currentPos.x * factor,
          y: currentPos.y * factor,
          z: currentPos.z * factor
        },
        { x: 0, y: 0, z: 0 }, // Always look at center
        500
      );
    }
  }, []);

  const handleResetView = useCallback(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      // Calculate center and reset view
      let sumX = 0, sumY = 0, sumZ = 0;
      graphData.nodes.forEach((node: any) => {
        sumX += node.x || 0;
        sumY += node.y || 0;
        sumZ += node.z || 0;
      });
      
      const centerX = sumX / graphData.nodes.length;
      const centerY = sumY / graphData.nodes.length;
      const centerZ = sumZ / graphData.nodes.length;
      
      fgRef.current.cameraPosition(
        { x: centerX, y: centerY, z: centerZ + 450 }, // Consistent distance for larger graph
        { x: centerX, y: centerY, z: centerZ },
        1000
      );
      
      const controls = fgRef.current.controls();
      if (controls) {
        controls.target.set(centerX, centerY, centerZ);
        controls.update();
      }
    }
  }, [graphData.nodes]);

  const handleCenterGraph = useCallback(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      // Calculate the actual center of all nodes
      let sumX = 0, sumY = 0, sumZ = 0;
      graphData.nodes.forEach((node: any) => {
        sumX += node.x || 0;
        sumY += node.y || 0;
        sumZ += node.z || 0;
      });
      
      const centerX = sumX / graphData.nodes.length;
      const centerY = sumY / graphData.nodes.length;
      const centerZ = sumZ / graphData.nodes.length;
      
      // Position camera to look directly at the center with consistent distance
      fgRef.current.cameraPosition(
        { x: centerX, y: centerY, z: centerZ + 450 }, // Camera at proper distance for larger graph
        { x: centerX, y: centerY, z: centerZ }, // Look at center
        1000
      );
      
      // Update controls to focus on center
      const controls = fgRef.current.controls();
      if (controls) {
        controls.target.set(centerX, centerY, centerZ);
        controls.update();
      }
    }
  }, [graphData.nodes]);

  // Create gradient sphere for nodes - stunning visual effect!
  const createGradientSphere = useCallback((node: any) => {
    const isHovered = hoveredNode?.id === node.id;
    
    // Create canvas for gradient texture
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // Create radial gradient - stunning gradient effect!
      const gradient = ctx.createRadialGradient(128, 128, 20, 128, 128, 128);
      
      if (isHovered) {
        // Gold gradient when hovered - winner's touch!
        gradient.addColorStop(0, '#FFD700');    // Bright gold center
        gradient.addColorStop(0.5, '#FFA500');  // Orange mid
        gradient.addColorStop(1, '#FF6B35');    // Deep orange edge
      } else {
        // Beautiful cyan-to-emerald gradient - THIS IS YOUR WINNING LOOK!
        gradient.addColorStop(0, '#22D3EE');    // Bright cyan center
        gradient.addColorStop(0.4, '#14B8A6');  // Teal 
        gradient.addColorStop(0.7, '#10B981');  // Emerald
        gradient.addColorStop(1, '#059669');    // Deep emerald edge
      }
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 256, 256);
    }
    
    // Create sphere with gradient texture
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    const geometry = new THREE.SphereGeometry(8, 48, 48); // Higher resolution for smoother gradient
    const material = new THREE.MeshStandardMaterial({
      map: texture,
      emissive: isHovered ? 0xFFD700 : 0x14B8A6,
      emissiveIntensity: isHovered ? 0.4 : 0.15,
      metalness: 0.3,
      roughness: 0.4,
    });
    
    const sphere = new THREE.Mesh(geometry, material);
    
    // Ensure proper matrix update
    sphere.matrixAutoUpdate = true;
    sphere.updateMatrix();
    
    return sphere;
  }, [hoveredNode]);

  if (loading) {
    return (
      <div className="relative bg-gradient-to-br from-indigo-50/50 to-purple-50/50 rounded-xl border-2 border-indigo-200/50" style={{ height: '500px' }}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-indigo-600" />
            <p className="text-indigo-600 font-medium">Loading 3D knowledge graph...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="relative bg-gradient-to-br from-red-50/50 to-pink-50/50 rounded-xl border-2 border-red-200/50 p-8" style={{ height: '500px' }}>
        <div className="text-center">
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="relative bg-gradient-to-br from-indigo-50/50 to-purple-50/50 rounded-xl border-2 border-indigo-200/50" style={{ height: '500px' }}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600 font-medium">No chunks available yet</p>
            <p className="text-sm text-gray-500 mt-2">Add some context to see the knowledge graph</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="rounded-xl border-2 border-indigo-200/50 overflow-hidden relative" style={{ height: '500px' }}>
        {/* Stunning gradient mesh background - vibrant and modern */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-50 via-teal-50 to-emerald-50">
          {/* Animated gradient orbs */}
          <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-cyan-300/25 to-blue-400/25 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-br from-emerald-300/25 to-teal-400/25 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-br from-amber-300/20 to-orange-300/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          
          {/* Grid pattern overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080801a_1px,transparent_1px),linear-gradient(to_bottom,#8080801a_1px,transparent_1px)] bg-[size:40px_40px]"></div>
        </div>
        <div className="relative w-full h-full" style={{ cursor: hoveredLink ? 'move' : 'grab' }}>
          <ForceGraph3D
            ref={fgRef}
            graphData={graphData}
            nodeLabel="name"
            nodeThreeObject={createGradientSphere}
            nodeThreeObjectExtend={false}
            linkColor={(link: any) => {
              if (hoveredLink && (hoveredLink.source === link.source && hoveredLink.target === link.target)) {
                return 'rgba(251, 191, 36, 1)'; // Gold when hovered
              }
              return 'rgba(6, 182, 212, 0.5)'; // Cyan/Teal links
            }}
            linkWidth={(link: any) => {
              if (hoveredLink && (hoveredLink.source === link.source && hoveredLink.target === link.target)) {
                return 4; // Thicker when hovered
              }
              return 2.5;
            }}
            linkOpacity={0.7}
            linkDirectionalParticles={3}
            linkDirectionalParticleWidth={2.5}
            linkDirectionalParticleSpeed={0.006}
            linkDirectionalParticleColor={(link: any) => {
              if (hoveredLink && (hoveredLink.source === link.source && hoveredLink.target === link.target)) {
                return '#FBBF24'; // Gold particles when hovered
              }
              return '#06B6D4'; // Cyan particles
            }}
            linkHoverPrecision={8}
            onNodeHover={handleNodeHover}
            onNodeClick={handleNodeClick}
            onLinkHover={handleLinkHover}
            onNodeDrag={(node: any) => {
              // Release fixed position during drag for smooth movement
              node.fx = node.x;
              node.fy = node.y;
              node.fz = node.z;
            }}
            onNodeDragEnd={(node: any) => {
              // Fix position after drag
              node.fx = node.x;
              node.fy = node.y;
              node.fz = node.z;
            }}
            enableNodeDrag={true}
            enableNavigationControls={true}
            enablePointerInteraction={true}
            showNavInfo={false}
            backgroundColor="rgba(0, 0, 0, 0)"
            d3AlphaDecay={0.01}
            d3VelocityDecay={0.3}
            d3ForceConfig={{
              center: { x: 0, y: 0, z: 0, strength: 0.05 },
              charge: { strength: -50 }
            }}
            warmupTicks={200}
            cooldownTicks={400}
            controlType="orbit"
          />
        </div>
        
        {/* Zoom Controls - Vertically Stacked in Bottom Left */}
        <div className="absolute bottom-4 left-4 flex flex-col gap-2 z-20">
          <button
            onClick={handleZoomIn}
            className="p-2.5 bg-white/95 hover:bg-white backdrop-blur-sm rounded-lg shadow-xl border border-indigo-300/50 transition-all duration-200 hover:scale-110 active:scale-95 group"
            title="Zoom In"
          >
            <ZoomIn className="w-5 h-5 text-indigo-600 group-hover:text-indigo-700" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2.5 bg-white/95 hover:bg-white backdrop-blur-sm rounded-lg shadow-xl border border-indigo-300/50 transition-all duration-200 hover:scale-110 active:scale-95 group"
            title="Zoom Out"
          >
            <ZoomOut className="w-5 h-5 text-indigo-600 group-hover:text-indigo-700" />
          </button>
          <button
            onClick={handleCenterGraph}
            className="p-2.5 bg-white/95 hover:bg-white backdrop-blur-sm rounded-lg shadow-xl border border-indigo-300/50 transition-all duration-200 hover:scale-110 active:scale-95 group"
            title="Center Graph"
          >
            <Locate className="w-5 h-5 text-indigo-600 group-hover:text-indigo-700" />
          </button>
        </div>
      </div>

      {/* Chunk Details Tooltip */}
      {hoveredNode && chunkDetails && (
        <div className="absolute top-4 right-4 max-w-md bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl border border-indigo-200/50 p-5 z-10 animate-in fade-in slide-in-from-right-5 duration-200">
          <div className="flex items-start gap-3">
            <div className="w-3 h-3 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-full flex-shrink-0 mt-1 animate-pulse"></div>
            <div className="flex-1">
              <div className="mb-3">
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                  Chunk ID: {chunkDetails.chunk_id.substring(0, 8)}...
                </span>
              </div>
              <p className="text-sm text-gray-800 mb-3 font-medium leading-relaxed max-h-32 overflow-y-auto">
                {chunkDetails.content.length > 300 
                  ? chunkDetails.content.substring(0, 300) + '...' 
                  : chunkDetails.content}
              </p>
              <div className="space-y-1 text-xs text-gray-600">
                {chunkDetails.metadata?.source && (
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-500">Source:</span>
                    <span className="text-indigo-600 font-semibold">
                      {chunkDetails.metadata.source}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-500">Connections:</span>
                  <span className="text-purple-600 font-semibold">{chunkDetails.tags.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-500">Accessed:</span>
                  <span className="text-blue-600 font-semibold">{chunkDetails.accessed_count} times</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info & Controls */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <div>
            <span className="font-semibold">{graphData.nodes.length}</span> nodes • 
            <span className="font-semibold ml-1">{graphData.links.length}</span> connections
          </div>
        </div>
        <div className="bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 backdrop-blur-xl rounded-2xl p-5 border border-indigo-200/30 shadow-xl">
          <div className="text-xs font-bold text-indigo-900/60 uppercase tracking-wider mb-3">
            Interactive Controls
          </div>
          <div className="space-y-2.5">
            {/* Pan */}
            <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-r from-cyan-50/50 to-blue-50/50 border border-cyan-200/30 hover:border-cyan-300/50 transition-all group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <Move className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-xs font-bold text-gray-900">Pan Graph</div>
                <div className="text-[10px] text-gray-600">Drag on links</div>
              </div>
            </div>
            
            {/* Rotate */}
            <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-r from-indigo-50/50 to-purple-50/50 border border-indigo-200/30 hover:border-indigo-300/50 transition-all group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <RotateCw className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-xs font-bold text-gray-900">Rotate View</div>
                <div className="text-[10px] text-gray-600">Drag on space</div>
              </div>
            </div>
            
            {/* Focus */}
            <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-r from-purple-50/50 to-pink-50/50 border border-purple-200/30 hover:border-purple-300/50 transition-all group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <MousePointer2 className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-xs font-bold text-gray-900">Focus Node</div>
                <div className="text-[10px] text-gray-600">Click any node</div>
              </div>
            </div>
            
            {/* Drag Node */}
            <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-r from-emerald-50/50 to-teal-50/50 border border-emerald-200/30 hover:border-emerald-300/50 transition-all group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <Hand className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-xs font-bold text-gray-900">Move Node</div>
                <div className="text-[10px] text-gray-600">Drag to reposition</div>
              </div>
            </div>
            
            {/* Zoom */}
            <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-r from-amber-50/50 to-orange-50/50 border border-amber-200/30 hover:border-amber-300/50 transition-all group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <ZoomIn className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-xs font-bold text-gray-900">Zoom In/Out</div>
                <div className="text-[10px] text-gray-600">Scroll or use buttons</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
