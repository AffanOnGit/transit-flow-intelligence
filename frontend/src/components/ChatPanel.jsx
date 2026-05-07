import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Command } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', { message: input });
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Network error. Please ensure the backend server is operational." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ x: 20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-96 h-screen glass-sidebar flex flex-col z-20"
    >
      <div className="p-6 border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary-500/20 p-2 rounded-xl border border-primary-500/30">
              <Sparkles className="text-primary-400 w-5 h-5" />
            </div>
            <div>
              <h3 className="text-white text-sm font-black tracking-tight uppercase">AI Navigator</h3>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                <p className="text-slate-500 text-[9px] font-bold uppercase tracking-widest">Knowledge Base Active</p>
              </div>
            </div>
          </div>
          <Command className="w-4 h-4 text-slate-700" />
        </div>
      </div>

      <div className="flex-grow overflow-y-auto p-6 space-y-6 custom-scrollbar" ref={scrollRef}>
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-12 px-4"
            >
              <div className="w-16 h-16 bg-slate-900 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-white/5 shadow-2xl">
                <Bot className="w-8 h-8 text-slate-700" />
              </div>
              <h4 className="text-white text-sm font-bold mb-2">How can I assist your travel?</h4>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                Query route durations, discover optimal transfers, or ask about specific stops in the CDA network.
              </p>
              
              <div className="mt-8 grid grid-cols-1 gap-2">
                {['How to get to FAST?', 'Route FR-01 path', 'Throughput to NUST'].map((prompt) => (
                  <button 
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    className="text-left px-4 py-2.5 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-slate-400 hover:bg-white/[0.05] hover:text-white transition-all"
                  >
                    "{prompt}"
                  </button>
                ))}
              </div>
            </motion.div>
          )}
          
          {messages.map((msg, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={i} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[90%] p-4 rounded-2xl text-[13px] leading-relaxed shadow-lg ${
                msg.role === 'user' 
                  ? 'bg-primary-600 text-white rounded-tr-none' 
                  : 'bg-slate-900 border border-white/10 text-slate-300 rounded-tl-none'
              }`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
          
          {isLoading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-slate-900 border border-white/5 p-4 rounded-2xl rounded-tl-none flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
                <span className="text-slate-500 text-[11px] font-bold uppercase tracking-widest">Processing Query...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="p-6 bg-slate-950/50 border-t border-white/5">
        <div className="relative group">
          <input 
            type="text" 
            placeholder="Search network or plan trip..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            className="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-5 pr-14 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/40 transition-all text-white placeholder:text-slate-600 group-hover:border-slate-700 shadow-inner"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="absolute right-2.5 top-2.5 w-10 h-10 flex items-center justify-center bg-primary-600 text-white rounded-xl hover:bg-primary-500 transition-all disabled:opacity-50 disabled:grayscale shadow-lg shadow-primary-900/20 active:scale-95"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[9px] text-slate-700 mt-4 text-center uppercase font-bold tracking-widest">Grounded in verified CDA datasets</p>
      </div>
    </motion.div>
  );
};

export default ChatPanel;
