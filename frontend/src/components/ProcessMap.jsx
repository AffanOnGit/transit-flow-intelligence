import React, { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';

const ProcessMap = ({ elements }) => {
  const cyRef = useRef(null);

  const stylesheet = [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'color': '#cbd5e1',
        'background-color': '#0ea5e9',
        'font-size': '10px',
        'width': '18px',
        'height': '18px',
        'border-width': '3px',
        'border-color': '#020617',
        'text-valign': 'bottom',
        'text-margin-y': 8,
        'font-weight': '700',
        'text-background-opacity': 0.8,
        'text-background-color': '#020617',
        'text-background-padding': '2px',
        'text-background-shape': 'roundrectangle'
      }
    },
    {
      selector: 'edge',
      style: {
        'label': 'data(label)',
        'width': 2,
        'line-color': '#334155',
        'target-arrow-color': '#334155',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'font-size': '9px',
        'color': '#94a3b8',
        'text-rotation': 'autorotate',
        'text-margin-y': -12,
        'opacity': 0.7,
        'font-weight': '600'
      }
    },
    {
      selector: 'edge[?is_bottleneck]',
      style: {
        'line-color': '#f43f5e',
        'line-style': 'dashed',
        'width': 5,
        'target-arrow-color': '#f43f5e',
        'opacity': 1,
        'color': '#fb7185',
        'font-size': '11px',
        'font-weight': '800'
      }
    },
    {
      selector: 'node:selected',
      style: {
        'background-color': '#fbbf24',
        'width': '24px',
        'height': '24px',
        'color': '#fbbf24',
        'border-color': '#fff'
      }
    }
  ];

  useEffect(() => {
    if (cyRef.current) {
      cyRef.current.fit();
      cyRef.current.on('mouseover', 'node', (e) => {
        e.target.style({ 'width': '22px', 'height': '22px', 'transition-duration': '0.2s' });
      });
      cyRef.current.on('mouseout', 'node', (e) => {
        e.target.style({ 'width': '18px', 'height': '18px' });
      });
    }
  }, [elements]);

  return (
    <div className="w-full h-full relative cytoscape-container">
      <CytoscapeComponent 
        elements={elements} 
        style={{ width: '100%', height: '100%' }} 
        stylesheet={stylesheet}
        cy={(cy) => { cyRef.current = cy }}
        layout={{ name: 'preset', animate: true, padding: 50 }}
      />
      
      {/* Visual Legend */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 flex items-center gap-6 px-6 py-3 bg-slate-900/40 backdrop-blur-md border border-white/10 rounded-full shadow-2xl z-10">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-primary-500 shadow-[0_0_8px_rgba(14,165,233,0.5)]"></div>
          <span className="text-[10px] text-slate-400 font-black uppercase tracking-widest">Transit Node</span>
        </div>
        <div className="w-px h-3 bg-white/10"></div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-1 bg-slate-600 rounded-full"></div>
          <span className="text-[10px] text-slate-400 font-black uppercase tracking-widest">Nominal Flow</span>
        </div>
        <div className="w-px h-3 bg-white/10"></div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-1 bg-rose-500 border-t border-dashed border-rose-500"></div>
          <span className="text-[10px] text-rose-400 font-black uppercase tracking-widest">Critical Delay</span>
        </div>
      </div>

      {/* Floating Instructions */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-slate-500 text-[10px] font-bold uppercase tracking-[0.2em] pointer-events-none opacity-40">
        Interactive Network Mesh — Zoom to Inspect Nodes
      </div>
    </div>
  );
};

export default ProcessMap;
