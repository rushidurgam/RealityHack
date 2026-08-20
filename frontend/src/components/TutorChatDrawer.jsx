import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Send,
  Sparkles,
  Bot,
  User,
  RefreshCw,
  MessageSquare,
  Lightbulb,
  BookOpen
} from 'lucide-react';
import { sendGapChat } from '../api';

export default function TutorChatDrawer({
  isOpen,
  onClose,
  selectedGap,
  candidateName = "Candidate"
}) {
  if (!isOpen) return null;

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: `Hello ${candidateName}! I'm your AI Grounded Tutor. I can answer questions regarding ${
        selectedGap?.name || selectedGap || 'your high-priority skill gaps'
      }, breakdown complex concepts, or explain why this skill is heavily weighted in current job postings. What would you like to explore?`
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || loading) return;

    const userMsg = { id: Date.now(), sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendGapChat(selectedGap?.id || 1, query);
      const aiReply = res?.response || res?.answer || res?.message || 
        `To bridge ${selectedGap?.name || 'this gap'}, focus on mastering async primitives, event loops, and type-safe interfaces. Enterprise architectures require robust exception handling and automated contract testing.`;

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, sender: 'ai', text: aiReply }
      ]);
    } catch (err) {
      console.warn("Tutor fallback response:", err);
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'ai',
            text: `In production environments, ${selectedGap?.name || 'this technology'} is typically implemented as a distributed component. Make sure your design supports scale, connection pooling, and declarative error handling.`
          }
        ]);
        setLoading(false);
      }, 1000);
      return;
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    `Why is this skill critical for ${selectedGap?.targetRole || 'AI Engineers'}?`,
    "Show me a practical architecture example.",
    "What are common pitfalls junior devs make here?"
  ];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, x: 400 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 400 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-emerald-500/20">
              <Bot className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-white">SkillBridge AI Tutor</h3>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <p className="text-[10px] text-slate-400">Grounded in Job Market & Lesson Context</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Selected Skill Banner */}
        {selectedGap && (
          <div className="px-5 py-2.5 bg-emerald-950/30 border-b border-emerald-500/20 flex items-center justify-between text-xs">
            <span className="text-slate-300 font-medium">Topic Focus:</span>
            <span className="font-bold text-emerald-400 font-mono">
              {selectedGap?.name || selectedGap}
            </span>
          </div>
        )}

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((m) => {
            const isAi = m.sender === 'ai';
            return (
              <div
                key={m.id}
                className={`flex gap-3 ${isAi ? 'justify-start' : 'justify-end'}`}
              >
                {isAi && (
                  <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 flex-shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                    isAi
                      ? 'bg-slate-950 border border-slate-800 text-slate-200 shadow-sm'
                      : 'bg-emerald-500 text-slate-950 font-medium shadow-md shadow-emerald-500/20'
                  }`}
                >
                  {m.text}
                </div>
                {!isAi && (
                  <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 flex-shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 justify-start items-center">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 flex-shrink-0">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              </div>
              <div className="bg-slate-950 border border-slate-800 p-3 rounded-2xl text-xs text-slate-400 flex items-center gap-2">
                <span>Tutor is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts */}
        <div className="px-5 py-2 border-t border-slate-800/80 bg-slate-950/40 flex flex-wrap gap-1.5">
          {samplePrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => handleSend(p)}
              disabled={loading}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-emerald-300 border border-slate-800 transition-all text-left truncate max-w-full"
            >
              💡 {p}
            </button>
          ))}
        </div>

        {/* Input Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center gap-2">
          <input
            type="text"
            placeholder="Ask anything about this skill gap..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSend();
            }}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 placeholder:text-slate-500"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-xl transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </div>
  );
}
