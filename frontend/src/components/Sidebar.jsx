import React from 'react';
import { Bus, Activity, AlertTriangle, TrendingUp, Filter, Settings2 } from 'lucide-react';
import { motion } from 'framer-motion';

const Sidebar = ({ routes, currentRoute, setCurrentRoute, threshold, setThreshold, stats }) => {
  return (
    <motion.div 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-80 h-screen glass-sidebar flex flex-col p-6 z-20"
    >
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-primary-500 p-2 rounded-xl shadow-lg shadow-primary-500/20">
            <Bus className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight text-white leading-none">TRANSIT<span className="text-primary-500">FLOW</span></h1>
            <p className="text-slate-500 text-[10px] uppercase tracking-[0.2em] font-bold mt-1">Intelligence System</p>
          </div>
        </div>
      </div>

      <div className="space-y-10 flex-grow overflow-y-auto pr-2 custom-scrollbar">
        {/* Route Filter */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-3.5 h-3.5 text-primary-400" />
            <label className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Network Filter</label>
          </div>
          <div className="relative group">
            <select 
              value={currentRoute}
              onChange={(e) => setCurrentRoute(e.target.value)}
              className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all text-white appearance-none cursor-pointer group-hover:border-white/20"
            >
              <option value="All">Global Network View</option>
              {routes.map(r => (
                <option key={r} value={r}>Route Segment {r}</option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
              <Settings2 className="w-4 h-4" />
            </div>
          </div>
        </section>

        {/* Bottleneck Slider */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-primary-400" />
              <label className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Latency Sensitivity</label>
            </div>
            <span className="bg-primary-500/10 text-primary-400 px-2 py-0.5 rounded text-[10px] font-mono border border-primary-500/20">{threshold}x</span>
          </div>
          <input 
            type="range" 
            min="1.0" max="3.0" step="0.1" 
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary-500"
          />
          <div className="flex justify-between text-[9px] text-slate-600 mt-3 font-bold uppercase tracking-tighter">
            <span>High Precision</span>
            <span>Broad View</span>
          </div>
        </section>

        {/* Stats Summary */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Performance Metrics</h3>
          </div>
          <div className="grid grid-cols-1 gap-3">
            <div className="bg-white/[0.02] border border-white/5 p-4 rounded-2xl hover:bg-white/[0.04] transition-colors">
              <div className="text-slate-500 text-[10px] uppercase font-bold tracking-tight mb-1">Mean Trip Duration</div>
              <div className="text-white text-xl font-bold tracking-tight">{stats?.summary?.avg || '---'}</div>
            </div>
            <div className="bg-white/[0.02] border border-white/5 p-4 rounded-2xl hover:bg-white/[0.04] transition-colors">
              <div className="text-slate-500 text-[10px] uppercase font-bold tracking-tight mb-1">Peak Efficiency</div>
              <div className="text-emerald-400 text-xl font-bold tracking-tight">{stats?.summary?.min || '---'}</div>
            </div>
          </div>
        </section>

        {/* Critical Bottlenecks */}
        <section className="space-y-4 pb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
            <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Network Congestion</h3>
          </div>
          <div className="space-y-3">
            {stats?.bottlenecks?.length > 0 ? (
              stats.bottlenecks.map((b, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  key={i} 
                  className="bg-rose-500/5 border border-rose-500/20 p-3 rounded-xl"
                >
                  <div className="flex justify-between items-start mb-1">
                    <div className="text-white text-[11px] font-bold truncate max-w-[140px]">{b.from_stop} → {b.to_stop}</div>
                    <div className="text-rose-500 text-[9px] font-black uppercase tracking-tighter">Delay</div>
                  </div>
                  <div className="text-rose-400/70 text-[10px] font-mono">{b.label} transition time</div>
                </motion.div>
              ))
            ) : (
              <div className="bg-emerald-500/5 border border-emerald-500/10 p-4 rounded-xl text-center">
                <p className="text-emerald-500/60 text-[10px] font-bold uppercase tracking-widest italic">Optimal Flow Detected</p>
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="mt-auto pt-6 border-t border-white/5 flex items-center justify-between">
        <span className="text-slate-600 text-[9px] font-bold uppercase tracking-widest">Build v2.4.0</span>
        <div className="flex gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-slate-500 text-[9px] font-bold uppercase tracking-widest">System Live</span>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;
