import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ProcessMap from './components/ProcessMap';
import ChatPanel from './components/ChatPanel';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [routes, setRoutes] = useState([]);
  const [currentRoute, setCurrentRoute] = useState('All');
  const [threshold, setThreshold] = useState(1.5);
  const [mapElements, setMapElements] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/routes`)
      .then(res => setRoutes(res.data))
      .catch(err => console.error("Failed to fetch routes", err));
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [mapRes, statsRes] = await Promise.all([
          axios.get(`${API_BASE}/map`, { params: { route_id: currentRoute, threshold } }),
          axios.get(`${API_BASE}/stats`, { params: { route_id: currentRoute, threshold } })
        ]);
        setMapElements(mapRes.data);
        setStats(statsRes.data);
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        // Add a slight artificial delay for smoother transitions
        setTimeout(() => setIsLoading(false), 300);
      }
    };

    fetchData();
  }, [currentRoute, threshold]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#020617] text-slate-200">
      {/* Background Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-900/10 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-rose-900/10 blur-[120px] rounded-full pointer-events-none"></div>

      <Sidebar 
        routes={routes}
        currentRoute={currentRoute}
        setCurrentRoute={setCurrentRoute}
        threshold={threshold}
        setThreshold={setThreshold}
        stats={stats}
      />
      
      <main className="flex-grow relative overflow-hidden">
        <AnimatePresence>
          {isLoading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-md"
            >
              <div className="flex flex-col items-center gap-6">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-primary-500/20 rounded-full"></div>
                  <div className="absolute top-0 w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div className="text-center">
                  <p className="text-primary-400 text-[10px] font-black uppercase tracking-[0.3em] mb-1">Synchronizing</p>
                  <p className="text-slate-500 text-[9px] font-bold uppercase tracking-widest">CDA Network Topology</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <motion.div 
          initial={{ opacity: 0, scale: 1.02 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full h-full"
        >
          <ProcessMap elements={mapElements} />
        </motion.div>
      </main>

      <ChatPanel />
    </div>
  );
}

export default App;
