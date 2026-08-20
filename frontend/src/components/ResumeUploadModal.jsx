import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  X,
  UploadCloud,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  Briefcase,
  User,
  Globe,
  Coins
} from 'lucide-react';
import { createUser } from '../api';
import { COUNTRIES, findCountry } from '../data/countries';

export default function ResumeUploadModal({
  isOpen,
  onClose,
  onAnalysisComplete,
  showToast
}) {
  if (!isOpen) return null;

  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [candidateName, setCandidateName] = useState('');
  const [position, setPosition] = useState('AI Fullstack Systems Engineer');
  const [selectedCountry, setSelectedCountry] = useState('United States');
  const [isProcessing, setIsProcessing] = useState(false);
  const [stepMessage, setStepMessage] = useState('');

  const activeCountryInfo = findCountry(selectedCountry);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !candidateName.trim()) {
      if (showToast) showToast('Please select a resume file (PDF/DOCX) or enter a candidate name.');
      return;
    }

    setIsProcessing(true);
    setStepMessage('Uploading resume document & parsing text structure...');

    try {
      const countryData = findCountry(selectedCountry);
      
      const formData = new FormData();
      formData.append("name", candidateName.trim() || file?.name.replace(/\.[^/.]+$/, "") || "New Candidate");
      formData.append("target_role", position.trim());
      formData.append("position", position.trim());
      formData.append("country", countryData.name);
      formData.append("country_code", countryData.code);
      formData.append("currency", countryData.currency);
      formData.append("currency_code", countryData.currencyCode);
      formData.append("currency_symbol", countryData.symbol);
      
      if (file) {
        formData.append("file", file);
      }

      setStepMessage('Extracting technical competencies & running Gemini AI multi-model evaluation...');
      const userRes = await createUser(formData);

      setStepMessage('Analysis finalized!');
      if (showToast) {
        showToast(`✨ Real-time AI Analysis complete for ${userRes.name} (${countryData.name})!`);
      }

      if (onAnalysisComplete) {
        onAnalysisComplete({
          user: userRes,
        });
      }
      onClose();
    } catch (err) {
      console.error("Resume analysis error:", err);
      if (showToast) {
        showToast(`⚠️ Failed to analyze resume: ${err.message || 'Server error'}`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden p-6 sm:p-8 space-y-6 max-h-[92vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Upload Candidate CV or Resume</h2>
              <p className="text-xs text-slate-400">Extract technical skills and generate live Gemini AI diagnostic insights</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-emerald-400" />
              Candidate Name
            </label>
            <input
              type="text"
              placeholder="e.g. Rahul Sharma"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 placeholder:text-slate-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
              Target Position / Job Title
            </label>
            <input
              type="text"
              placeholder="e.g. AI Fullstack Systems Engineer"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 placeholder:text-slate-600"
            />
          </div>

          {/* Country Selection */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-cyan-400" />
                Country / Region
              </label>
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                {COUNTRIES.map((c) => (
                  <option key={c.code} value={c.name}>
                    {c.name} ({c.code})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Coins className="w-3.5 h-3.5 text-amber-400" />
                Auto-Mapped Currency
              </label>
              <div className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-amber-300 font-medium flex items-center justify-between">
                <span>{activeCountryInfo.currency} ({activeCountryInfo.currencyCode})</span>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">{activeCountryInfo.symbol}</span>
              </div>
            </div>
          </div>

          {/* Dropzone */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">CV or Resume Document (.PDF, .DOCX, .TXT)</label>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                file
                  ? 'border-emerald-500/50 bg-emerald-950/20'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-950/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileChange}
                className="hidden"
              />

              {file ? (
                <div className="flex items-center justify-center gap-3 text-emerald-400">
                  <FileText className="w-6 h-6" />
                  <div className="text-left">
                    <p className="font-semibold text-xs text-white">{file.name}</p>
                    <p className="text-[10px] text-slate-400">{(file.size / 1024).toFixed(1)} KB — Click to change</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <UploadCloud className="w-8 h-8 text-slate-500 mx-auto" />
                  <p className="text-xs text-slate-300 font-medium">
                    Drag and drop your CV or resume, or <span className="text-emerald-400">browse files</span>
                  </p>
                  <p className="text-[10px] text-slate-500">Supports PDF or Word (.docx) with real text extraction</p>
                </div>
              )}
            </div>
          </div>

          {/* Progress Status */}
          {isProcessing && (
            <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300 flex items-center gap-2.5">
              <RefreshCw className="w-4 h-4 animate-spin text-emerald-400 flex-shrink-0" />
              <span>{stepMessage}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isProcessing}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-all"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isProcessing}
              className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Analyzing Profile...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Run Gemini AI Evaluation
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
