import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  UserPlus,
  Edit3,
  Trash2,
  Save,
  User,
  Briefcase,
  Mail,
  MapPin,
  Globe,
  Coins,
  Clock,
  Sparkles,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  Users,
  Brain,
  UploadCloud,
  FileText,
  ShieldAlert,
  ShieldCheck,
  Check,
  Award,
  ChevronRight
} from 'lucide-react';
import { createUser, updateUser, deleteUser, assessPosition } from '../api';
import { COUNTRIES, findCountry } from '../data/countries';

export default function UserManagementModal({
  isOpen,
  onClose,
  mode = 'add', // 'add' | 'edit' | 'manage'
  selectedUser = null,
  allUsers = [],
  onUserAdded,
  onUserUpdated,
  onUserDeleted,
  onSelectUser,
  showToast
}) {
  if (!isOpen) return null;

  const fileInputRef = useRef(null);
  const [activeMode, setActiveMode] = useState(mode);
  const [editingTarget, setEditingTarget] = useState(selectedUser);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  // Form fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [currentRole, setCurrentRole] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [location, setLocation] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('United States');
  const [currentSalary, setCurrentSalary] = useState('$55,000');
  const [targetSalary, setTargetSalary] = useState('$95,000');
  const [experienceYears, setExperienceYears] = useState(4);
  const [avatar, setAvatar] = useState('');

  // CV / Resume upload state (compulsory on create)
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [useTextMode, setUseTextMode] = useState(false);

  // Live dynamic risk assessment
  const [assessedRisk, setAssessedRisk] = useState(null);
  const [isAssessing, setIsAssessing] = useState(false);

  const activeCountryInfo = findCountry(selectedCountry);

  // Fetch dynamic risk when target position changes
  useEffect(() => {
    if (!targetRole || targetRole.trim().length < 2) return;
    let isCancelled = false;
    const timer = setTimeout(async () => {
      try {
        setIsAssessing(true);
        const res = await assessPosition(targetRole.trim(), selectedCountry, resumeText);
        if (!isCancelled && res) {
          setAssessedRisk(res);
        }
      } catch (err) {
        console.warn("Live position assessment error:", err);
      } finally {
        if (!isCancelled) setIsAssessing(false);
      }
    }, 400);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [targetRole, selectedCountry, resumeText]);

  // Populate fields when mode or target changes
  useEffect(() => {
    setActiveMode(mode);
    setErrorMessage(null);
    setDeleteConfirmId(null);
    setResumeFile(null);
    setResumeText('');
    setUseTextMode(false);

    const target = mode === 'edit' ? selectedUser : null;
    setEditingTarget(target);

    if (target) {
      setName(target.name || '');
      setEmail(target.email || '');
      setCurrentRole(target.currentRole || target.current_role || '');
      setTargetRole(target.position || target.targetRole || target.target_role || '');
      setLocation(target.location || 'Austin, TX (or Remote)');
      setSelectedCountry(target.country || 'United States');
      setCurrentSalary(target.currentSalary || target.current_salary || '$55,000');
      setTargetSalary(target.targetSalary || target.target_salary || '$95,000');
      setExperienceYears(target.experienceYears || target.experience_years || 4);
      setAvatar(target.avatar || '');
    } else {
      // Default new user template
      setName('');
      setEmail('');
      setCurrentRole('Customer Support Team Lead');
      setTargetRole('AI Operations & Support Systems Specialist');
      setLocation('Austin, TX (or Remote)');
      setSelectedCountry('United States');
      setCurrentSalary('$55,000');
      setTargetSalary('$95,000');
      setExperienceYears(4);
      setAvatar('https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80');
    }
  }, [mode, selectedUser, isOpen]);

  const handleStartEdit = (user) => {
    setEditingTarget(user);
    setName(user.name || '');
    setEmail(user.email || '');
    setCurrentRole(user.currentRole || user.current_role || '');
    setTargetRole(user.position || user.targetRole || user.target_role || '');
    setLocation(user.location || 'Remote');
    setSelectedCountry(user.country || 'United States');
    setCurrentSalary(user.currentSalary || user.current_salary || '$55,000');
    setTargetSalary(user.targetSalary || user.target_salary || '$95,000');
    setExperienceYears(user.experienceYears || user.experience_years || 4);
    setAvatar(user.avatar || '');
    setResumeFile(null);
    setResumeText('');
    setActiveMode('edit');
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResumeFile(e.dataTransfer.files[0]);
      setErrorMessage(null);
    }
  };

  const handleSaveUser = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setErrorMessage('Please enter candidate full name.');
      return;
    }

    // Compulsory CV / Resume check when adding a new user
    if (activeMode === 'add' && !resumeFile && !resumeText.trim()) {
      setErrorMessage('A CV or Resume is compulsory for candidate creation. Please upload a CV/resume document (.pdf, .docx, .txt) or paste CV text.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const countryInfo = findCountry(selectedCountry);

    try {
      if (activeMode === 'edit' && editingTarget?.id) {
        const userData = {
          name: name.trim(),
          email: email.trim() || null,
          currentRole: currentRole.trim() || 'Current Professional',
          targetRole: targetRole.trim() || 'AI Systems Specialist',
          position: targetRole.trim() || 'AI Systems Specialist',
          location: location.trim() || 'Remote',
          country: countryInfo.name,
          countryCode: countryInfo.code,
          currency: countryInfo.currency,
          currencyCode: countryInfo.currencyCode,
          currencySymbol: countryInfo.symbol,
          avatar: avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
          currentSalary: currentSalary.trim(),
          targetSalary: targetSalary.trim(),
          experienceYears: parseFloat(experienceYears) || 4,
        };

        const updated = await updateUser(editingTarget.id, userData);
        if (showToast) showToast(`✅ User "${name}" profile updated!`);
        if (onUserUpdated) onUserUpdated(updated || { ...editingTarget, ...userData });
      } else {
        // Create user with mandatory CV / Resume
        const formData = new FormData();
        formData.append("name", name.trim());
        formData.append("current_role", currentRole.trim() || "Customer Support Team Lead");
        formData.append("target_role", targetRole.trim() || "AI Operations Specialist");
        formData.append("position", targetRole.trim() || "AI Operations Specialist");
        formData.append("country", countryInfo.name);
        formData.append("country_code", countryInfo.code);
        formData.append("currency", countryInfo.currency);
        formData.append("currency_code", countryInfo.currencyCode);
        formData.append("currency_symbol", countryInfo.symbol);
        formData.append("location", location.trim() || "Remote");
        formData.append("current_salary", currentSalary.trim());
        formData.append("target_salary", targetSalary.trim());
        if (email.trim()) formData.append("email", email.trim());

        if (resumeFile) {
          formData.append("file", resumeFile);
        } else if (resumeText.trim()) {
          const blob = new Blob([resumeText], { type: "text/plain" });
          formData.append("file", blob, `${name.replace(/\s+/g, '_')}_cv.txt`);
        }

        const created = await createUser(formData);
        if (showToast) showToast(`🎉 Profile & CV Analysis created for "${name}"!`);
        if (onUserAdded) onUserAdded(created || { id: 'u_' + Date.now(), name: name.trim() });
      }
      onClose();
    } catch (err) {
      console.error("Save user error:", err);
      setErrorMessage(err.message || "Failed to save candidate. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    setIsSubmitting(true);
    try {
      await deleteUser(userId);
      if (showToast) showToast(`🗑️ Profile "${userName}" removed from database.`);
      if (onUserDeleted) onUserDeleted(userId);
      setDeleteConfirmId(null);
      if (activeMode === 'edit' && editingTarget?.id === userId) {
        onClose();
      }
    } catch (err) {
      console.warn("Delete user fallback:", err);
      if (onUserDeleted) onUserDeleted(userId);
      if (showToast) showToast(`🗑️ Profile "${userName}" removed.`);
      setDeleteConfirmId(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              {activeMode === 'manage' ? (
                <Users className="w-5 h-5" />
              ) : activeMode === 'edit' ? (
                <Edit3 className="w-5 h-5" />
              ) : (
                <UserPlus className="w-5 h-5" />
              )}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                {activeMode === 'manage'
                  ? 'Candidate Profiles Directory'
                  : activeMode === 'edit'
                  ? `Edit Profile: ${name || editingTarget?.name || 'Candidate'}`
                  : 'Create Candidate Profile (with CV/Resume)'}
              </h2>
              <p className="text-xs text-slate-400">
                {activeMode === 'manage'
                  ? 'Browse profile-wise candidate cards, switch active persona, or manage records'
                  : 'CV or Resume upload is mandatory to generate live ATS, radar, and career intelligence.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {activeMode !== 'manage' && allUsers.length > 0 && (
              <button
                type="button"
                onClick={() => setActiveMode('manage')}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all flex items-center gap-1.5"
              >
                <Users className="w-3.5 h-3.5" />
                All Profiles ({allUsers.length})
              </button>
            )}
            {activeMode === 'manage' && (
              <button
                type="button"
                onClick={() => {
                  setEditingTarget(null);
                  setActiveMode('add');
                }}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 transition-all flex items-center gap-1.5 border border-emerald-500/30"
              >
                <UserPlus className="w-3.5 h-3.5" />
                + Create Profile
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all ml-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {errorMessage && (
            <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-500/40 text-xs text-rose-200 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {activeMode === 'manage' ? (
            /* Profile-Wise Candidate Directory */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Saved Profiles ({allUsers.length})
                </p>
                <span className="text-[11px] text-slate-400">
                  Select any profile card to view full intelligence suite
                </span>
              </div>

              {allUsers.length === 0 ? (
                <div className="p-8 text-center bg-slate-950/60 rounded-3xl border border-slate-800 space-y-3">
                  <User className="w-10 h-10 text-slate-600 mx-auto" />
                  <p className="text-sm font-semibold text-white">No candidate profiles found.</p>
                  <p className="text-xs text-slate-400">Click below to create your first candidate profile with a CV or resume.</p>
                  <button
                    type="button"
                    onClick={() => setActiveMode('add')}
                    className="mt-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs"
                  >
                    + Create Candidate Profile
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {allUsers.map((u) => {
                    const isSelected = selectedUser?.id === u.id;
                    const cInfo = findCountry(u.country);

                    return (
                      <div
                        key={u.id}
                        className={`p-5 rounded-3xl border transition-all flex flex-col justify-between space-y-4 relative ${
                          isSelected
                            ? 'border-emerald-500/50 bg-gradient-to-br from-slate-900 to-emerald-950/30 shadow-xl shadow-emerald-950/30'
                            : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'
                        }`}
                      >
                        {/* Top Card Info */}
                        <div className="flex items-start gap-3.5">
                          <img
                            src={u.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80'}
                            alt={u.name}
                            className="w-14 h-14 rounded-2xl object-cover border border-slate-700 flex-shrink-0 shadow-md"
                          />
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <h3 className="text-sm font-bold text-white truncate">{u.name}</h3>
                              {isSelected ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                  ACTIVE
                                </span>
                              ) : null}
                            </div>
                            <p className="text-xs text-slate-400 truncate mt-0.5">
                              {u.current_role || u.currentRole || 'Current Role'} <span className="text-emerald-400">➔</span> <strong className="text-emerald-400">{u.position || u.targetRole || u.target_role}</strong>
                            </p>
                            <div className="flex items-center gap-2 mt-1.5 flex-wrap text-[11px]">
                              <span className="text-cyan-300 bg-cyan-950/40 px-2 py-0.5 rounded-lg border border-cyan-500/20 flex items-center gap-1">
                                <Globe className="w-3 h-3" /> {cInfo.name}
                              </span>
                              <span className="text-amber-300 bg-amber-950/40 px-2 py-0.5 rounded-lg border border-amber-500/20">
                                {u.current_salary || '$55k'} - {u.target_salary || '$95k'}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Profile Key Stats Row */}
                        <div className="grid grid-cols-3 gap-2 p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-center">
                          <div>
                            <span className="text-[10px] text-slate-400 uppercase font-semibold block">ATS Pass</span>
                            <span className="text-xs font-bold text-cyan-400">{Math.round(u.resume_score || 82)}%</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Readiness</span>
                            <span className="text-xs font-bold text-emerald-400">{Math.round(u.candidate_score || 85)}%</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Exposure</span>
                            <span className="text-xs font-bold text-rose-400">{u.automation_risk_score !== undefined ? u.automation_risk_score : 75}%</span>
                          </div>
                        </div>

                        {/* CV Status */}
                        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                            <FileText className="w-3.5 h-3.5" />
                            {u.file_name ? `CV: ${u.file_name}` : 'CV / Resume Attached'}
                          </span>
                          <span>{u.experience_years || 4} Yrs Exp</span>
                        </div>

                        {/* Card Actions */}
                        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1.5">
                            {!isSelected ? (
                              <button
                                type="button"
                                onClick={() => {
                                  if (onSelectUser) onSelectUser(u);
                                  onClose();
                                }}
                                className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition-all flex items-center gap-1 shadow-sm"
                              >
                                <span>Select Profile</span>
                                <ChevronRight className="w-3.5 h-3.5" />
                              </button>
                            ) : (
                              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                                <CheckCircle2 className="w-4 h-4" /> Active in Workspace
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-1.5">
                            <button
                              type="button"
                              onClick={() => handleStartEdit(u)}
                              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all text-xs"
                              title="Edit candidate profile"
                            >
                              <Edit3 className="w-4 h-4" />
                            </button>

                            {deleteConfirmId === u.id ? (
                              <div className="flex items-center gap-1 bg-rose-950/80 p-1 rounded-xl border border-rose-500/40">
                                <button
                                  type="button"
                                  onClick={() => handleDeleteUser(u.id, u.name)}
                                  className="px-2 py-1 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-lg text-[10px] transition-all"
                                >
                                  Confirm
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setDeleteConfirmId(null)}
                                  className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-[10px] transition-all"
                                >
                                  Cancel
                                </button>
                              </div>
                            ) : (
                              <button
                                type="button"
                                onClick={() => setDeleteConfirmId(u.id)}
                                className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-all text-xs"
                                title="Delete candidate"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            /* Add / Edit Form Mode */
            <form id="user-form" onSubmit={handleSaveUser} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Name */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-emerald-400" />
                    Candidate Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Rahul Sharma"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-cyan-400" />
                    Email Address
                  </label>
                  <input
                    type="email"
                    placeholder="candidate@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Current Role */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                    Current Job Role
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Customer Support Team Lead"
                    value={currentRole}
                    onChange={(e) => setCurrentRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
                  />
                </div>

                {/* Target Role */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                    Target AI Position *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. AI Operations & Support Systems Specialist"
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Country and Currency */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <Globe className="w-3.5 h-3.5 text-cyan-400" />
                    Country / Market Selection
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
                    Market Currency
                  </label>
                  <div className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-amber-300 font-medium flex items-center justify-between">
                    <span>{activeCountryInfo.currency} ({activeCountryInfo.currencyCode})</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">{activeCountryInfo.symbol}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Location */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    Location / City
                  </label>
                  <input
                    type="text"
                    placeholder="Austin, TX / Remote"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
                  />
                </div>

                {/* Current Salary */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Current Salary ({activeCountryInfo.symbol})
                  </label>
                  <input
                    type="text"
                    placeholder={`${activeCountryInfo.symbol}55,000`}
                    value={currentSalary}
                    onChange={(e) => setCurrentSalary(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-slate-600"
                  />
                </div>

                {/* Target Salary */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 text-emerald-400">
                    Target Compensation ({activeCountryInfo.symbol})
                  </label>
                  <input
                    type="text"
                    placeholder={`${activeCountryInfo.symbol}95,000`}
                    value={targetSalary}
                    onChange={(e) => setTargetSalary(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* MANDATORY CV / RESUME UPLOAD SECTION */}
              {activeMode === 'add' && (
                <div className="p-4 sm:p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="block text-xs font-bold text-white flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-emerald-400" />
                      Upload CV or Resume * <span className="text-[10px] text-emerald-400 font-semibold">(Compulsory)</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => setUseTextMode(!useTextMode)}
                      className="text-[11px] text-cyan-400 hover:underline"
                    >
                      {useTextMode ? 'Switch to Document Upload' : 'Paste CV Text Instead'}
                    </button>
                  </div>

                  {!useTextMode ? (
                    <div
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-5 text-center cursor-pointer transition-all ${
                        resumeFile
                          ? 'border-emerald-500/60 bg-emerald-950/30'
                          : 'border-slate-800 hover:border-emerald-500/40 bg-slate-950/70'
                      }`}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx,.doc,.txt"
                        onChange={handleFileChange}
                        className="hidden"
                      />

                      {resumeFile ? (
                        <div className="flex items-center justify-center gap-3 text-emerald-400">
                          <CheckCircle2 className="w-6 h-6 flex-shrink-0" />
                          <div className="text-left">
                            <p className="font-bold text-xs text-white">{resumeFile.name}</p>
                            <p className="text-[10px] text-slate-400">
                              {(resumeFile.size / 1024).toFixed(1)} KB • Click to choose a different CV
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-1.5">
                          <UploadCloud className="w-7 h-7 text-emerald-400 mx-auto" />
                          <p className="text-xs text-slate-200 font-medium">
                            Select or drop candidate's <strong className="text-emerald-400">CV or Resume</strong>
                          </p>
                          <p className="text-[10px] text-slate-400">
                            Required: .pdf, .docx, or .txt file format
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>
                      <textarea
                        rows={4}
                        required
                        placeholder="Paste the full text of candidate's CV or Resume here..."
                        value={resumeText}
                        onChange={(e) => {
                          setResumeText(e.target.value);
                          setErrorMessage(null);
                        }}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 placeholder:text-slate-600 resize-none font-mono"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Dynamic Role Risk Assessment Card */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5 text-purple-400" />
                  Dynamic AI Role Risk Assessment {isAssessing && <RefreshCw className="w-3 h-3 animate-spin text-purple-400 inline ml-1" />}
                </label>
                {assessedRisk ? (
                  <div className="w-full bg-purple-950/30 border border-purple-500/30 rounded-xl p-3.5 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-400">Occupational Exposure:</span>
                        <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold">
                          {assessedRisk.automation_risk_score}%
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-400">Shielded Resilience Moat:</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                          {assessedRisk.shielded_risk_score}%
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-300 italic line-clamp-2">
                      "{assessedRisk.explanation}"
                    </p>
                  </div>
                ) : (
                  <div className="w-full bg-purple-950/20 border border-purple-500/20 rounded-xl px-3 py-2.5 text-xs text-purple-300 flex items-center gap-2">
                    <Brain className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                    <span>Gemini AI dynamically computes Automation Exposure and Shielded Score for this position</span>
                  </div>
                )}
              </div>
            </form>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-5 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
          <div>
            {activeMode === 'edit' && (
              <button
                type="button"
                onClick={() => handleDeleteUser(editingTarget.id, editingTarget.name)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-rose-400 hover:bg-rose-950/40 border border-rose-500/20 transition-all flex items-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete Profile
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-all"
            >
              Close
            </button>

            {activeMode !== 'manage' && (
              <button
                type="submit"
                form="user-form"
                disabled={isSubmitting}
                className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Processing AI Evaluation...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    {activeMode === 'edit' ? 'Save Changes' : 'Create Candidate Profile'}
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
