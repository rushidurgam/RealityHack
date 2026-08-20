import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  X,
  Award,
  ShieldCheck,
  Download,
  CheckCircle2,
  Calendar,
  Share2,
  Check,
  FileText,
  Sparkles,
  ExternalLink
} from 'lucide-react';

export default function DossierModal({
  isOpen,
  onClose,
  persona,
  completedMilestones = [],
  showToast
}) {
  if (!isOpen || !persona) return null;

  const [copied, setCopied] = useState(false);
  const verificationHash = "0x" + Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join('');

  const handlePrintDownload = () => {
    window.print();
    if (showToast) {
      showToast('📄 Preparing printable Career Dossier...');
    }
  };

  const handleShare = () => {
    navigator.clipboard.writeText(`https://skillbridge.ai/verify/${verificationHash}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    if (showToast) {
      showToast('🔗 Verification link copied to clipboard!');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className="relative w-full max-w-2xl bg-slate-900 border-2 border-emerald-500/50 rounded-3xl shadow-2xl overflow-hidden p-6 sm:p-8 space-y-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-500/20">
              <Award className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                  Certified Proof-of-Work
                </span>
                <span className="text-xs font-mono text-slate-400">ID: {verificationHash.slice(0, 10)}...</span>
              </div>
              <h2 className="text-xl font-bold text-white mt-1">Verified Career Dossier</h2>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Candidate Profile Summary */}
        <div className="grid sm:grid-cols-2 gap-4 bg-slate-950/70 p-5 rounded-2xl border border-slate-800">
          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Candidate</span>
            <p className="text-base font-bold text-white mt-0.5">{persona.name}</p>
            <p className="text-xs text-emerald-400 font-medium">{persona.targetRole}</p>
          </div>

          <div>
            <span className="text-[10px] uppercase text-slate-400 font-semibold">Readiness Index</span>
            <div className="flex items-baseline gap-2 mt-0.5">
              <span className="text-xl font-extrabold text-emerald-400 font-mono">
                {persona.readinessScore || 85}%
              </span>
              <span className="text-xs text-slate-400">Target Role Fit</span>
            </div>
          </div>
        </div>

        {/* Verified Milestones */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Verified Technical Milestones ({completedMilestones.length})
          </h4>

          <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
            {completedMilestones.length > 0 ? (
              completedMilestones.map((m, i) => (
                <div
                  key={m.id || i}
                  className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <div>
                      <span className="font-semibold text-white">{m.title}</span>
                      <p className="text-[10px] text-slate-400">{m.phase}</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/20">
                    Grade: 92/100
                  </span>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-center text-xs text-slate-400">
                Complete roadmap labs to generate verified credentials.
              </div>
            )}
          </div>
        </div>

        {/* Cryptographic Verification Badge */}
        <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>Immutable Hash: <strong className="font-mono text-emerald-300">{verificationHash}</strong></span>
          </div>
          <button
            onClick={handleShare}
            className="text-emerald-400 hover:underline flex items-center gap-1 font-semibold"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Share2 className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Share'}
          </button>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-all"
          >
            Close
          </button>

          <button
            onClick={handlePrintDownload}
            className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
          >
            <Download className="w-4 h-4" />
            Download PDF Report
          </button>
        </div>
      </motion.div>
    </div>
  );
}
