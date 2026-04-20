import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LogOut, Upload, Trash2, Folder, ShieldCheck, Mail,
  Lock, Plus, File, Globe, User as UserIcon, EyeOff, Download
} from 'lucide-react';
import { authApi, driveApi } from './api';

function App() {
  const Motion = motion;
  const [token, setToken] = useState(localStorage.getItem('aura_token'));
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // App view state
  const [feedMode, setFeedMode] = useState('private'); // 'private' or 'public'
  const [userEmail, setUserEmail] = useState(localStorage.getItem('aura_email') || '');

  // Auth state
  const [authMode, setAuthMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [caption, setCaption] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const logout = useCallback(() => {
    localStorage.removeItem('aura_token');
    localStorage.removeItem('aura_token_id_hack');
    localStorage.removeItem('aura_email');
    setToken(null);
    setUserEmail('');
    setPosts([]);
  }, []);

  const loadFeed = useCallback(async () => {
    try {
      const res = await driveApi.getFeed(feedMode);
      setPosts(res.data.posts || []);
    } catch (error) {
      console.error(error);
      if (error.response?.status === 401) logout();
    }
  }, [feedMode, logout]);

  useEffect(() => {
    if (token) {
      const timer = window.setTimeout(() => {
        loadFeed();
      }, 0);
      return () => window.clearTimeout(timer);
    }
  }, [token, loadFeed]);

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (authMode === 'login') {
        const res = await authApi.login(email, password);
        localStorage.setItem('aura_token', res.data.access_token);

        // Fetch user details to get the persistent ID for delete permissions
        const userRes = await authApi.me();
        localStorage.setItem('aura_token_id_hack', userRes.data.id);
        localStorage.setItem('aura_email', userRes.data.email);

        setUserEmail(userRes.data.email);
        setToken(res.data.access_token);
        showNotification('Welcome to Aura Drive');
      } else {
        await authApi.register(email, password);
        showNotification('Registration successful! Please login.');
        setAuthMode('login');
      }
    } catch (error) {
      console.error(error);
      showNotification(error.response?.data?.detail || 'Authentication failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) return showNotification('Please select a file', 'error');
    try {
      setLoading(true);
      await driveApi.upload(uploadFile, caption, isPublic);
      showNotification('Asset stored securely');
      setUploadFile(null);
      setCaption('');
      setIsPublic(false);
      loadFeed();
    } catch (error) {
      console.error(error);
      showNotification('Upload failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('PERMANENT DELETE: This will erase the file from both your vault and the community. Continue?')) return;
    try {
      await driveApi.deletePost(id);
      showNotification('Asset erased permanently');
      loadFeed();
    } catch (error) {
      console.error(error);
      showNotification('Delete failed', 'error');
    }
  };

  const handleVisibilityToggle = async (id, currentStatus) => {
    const newStatus = !currentStatus;
    const action = newStatus ? 'Sharing with community...' : 'Moving to private vault...';
    try {
      showNotification(action);
      await driveApi.updateVisibility(id, newStatus);
      showNotification(newStatus ? 'Asset is now Public' : 'Asset is now Private');
      loadFeed();
    } catch (error) {
      console.error(error);
      showNotification('Visibility update failed', 'error');
    }
  };

  const handleDownload = (url, fileName) => {
    // We use the ik-attachment=true parameter to force ImageKit to trigger a download
    const downloadUrl = `${url}?ik-attachment=true`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = fileName || 'aura-asset';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showNotification('Download started');
  };

  const currentUserId = localStorage.getItem('aura_token_id_hack');

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem 2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 0', marginBottom: '2rem' }}>
        <Motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          style={{ fontSize: '1.6rem', fontWeight: 700, background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          AURA DRIVE
        </Motion.div>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          {token && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.05)', padding: '0.5rem 1rem', borderRadius: '10px' }}>
                <UserIcon size={14} />
                {userEmail}
              </div>
              <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '0.25rem' }}>
                <button
                  onClick={() => setFeedMode('private')}
                  className="btn"
                  style={{
                    padding: '0.5rem 1rem',
                    fontSize: '0.85rem',
                    background: feedMode === 'private' ? 'var(--accent-color)' : 'transparent',
                    color: feedMode === 'private' ? 'white' : 'var(--text-secondary)'
                  }}
                >
                  <Lock size={14} /> My Vault
                </button>
                <button
                  onClick={() => setFeedMode('public')}
                  className="btn"
                  style={{
                    padding: '0.5rem 1rem',
                    fontSize: '0.85rem',
                    background: feedMode === 'public' ? 'var(--accent-color)' : 'transparent',
                    color: feedMode === 'public' ? 'white' : 'var(--text-secondary)'
                  }}
                >
                  <Globe size={14} /> Community
                </button>
              </div>
              <button onClick={logout} className="btn" style={{ color: 'var(--text-secondary)' }}>
                <LogOut size={18} />
              </button>
            </>
          )}
        </div>
      </header>

      <AnimatePresence mode="wait">
        {!token ? (
          <Motion.div
            key="auth"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-card"
            style={{ maxWidth: '450px', margin: '4rem auto', padding: '2.5rem' }}
          >
            <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2rem' }}>
              {['login', 'register'].map(mode => (
                <span
                  key={mode}
                  onClick={() => setAuthMode(mode)}
                  style={{ cursor: 'pointer', fontWeight: 600, fontSize: '1.1rem', color: authMode === mode ? 'var(--text-primary)' : 'var(--text-secondary)', position: 'relative' }}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                  {authMode === mode && <Motion.div layoutId="underline" style={{ position: 'absolute', bottom: -5, left: 0, width: '100%', height: '3px', background: 'var(--accent-color)', borderRadius: '4px' }} />}
                </span>
              ))}
            </div>

            <form onSubmit={handleAuth}>
              <div style={{ marginBottom: '1.2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.6rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Email Address</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                  <input type="email" className="input-field" value={email} onChange={e => setEmail(e.target.value)} placeholder="name@company.com" required style={{ paddingLeft: '3rem' }} />
                </div>
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.6rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Password</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                  <input type="password" className="input-field" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required style={{ paddingLeft: '3rem' }} />
                </div>
              </div>
              <button disabled={loading} className="btn btn-primary" style={{ width: '100%' }}>
                {loading ? 'Processing...' : 'Continue'}
              </button>
            </form>
          </Motion.div>
        ) : (
          <Motion.div
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Upload Section */}
            <div className="glass-card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', padding: '2rem', marginBottom: '3rem' }}>
              <div>
                <h2 style={{ marginBottom: '0.5rem' }}>Cloud Deposit</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Securely upload and manage your premium assets.</p>
                <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div
                    onClick={() => setIsPublic(!isPublic)}
                    style={{
                      width: '40px', height: '24px', background: isPublic ? 'var(--accent-color)' : 'rgba(255,255,255,0.1)',
                      borderRadius: '20px', position: 'relative', cursor: 'pointer', transition: '0.3s'
                    }}
                  >
                    <Motion.div
                      animate={{ x: isPublic ? 18 : 2 }}
                      style={{ width: '20px', height: '20px', background: 'white', borderRadius: '50%', marginTop: '2px' }}
                    />
                  </div>
                  <span style={{ fontSize: '0.9rem', color: isPublic ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                    {isPublic ? <><Globe size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Public Link</> : <><Lock size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Private Vault</>}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div
                  onClick={() => document.getElementById('file-input').click()}
                  style={{ border: '2px dashed var(--glass-border)', padding: '1.5rem', borderRadius: '15px', textAlign: 'center', cursor: 'pointer', background: 'rgba(255,255,255,0.02)' }}
                >
                  <Upload size={24} style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }} />
                  <div style={{ fontSize: '0.9rem', color: uploadFile ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                    {uploadFile ? uploadFile.name : 'Click to select file'}
                  </div>
                  <input type="file" id="file-input" style={{ display: 'none' }} onChange={e => setUploadFile(e.target.files[0])} />
                </div>
                <input type="text" className="input-field" placeholder="Asset caption..." value={caption} onChange={e => setCaption(e.target.value)} />
                <button onClick={handleUpload} disabled={loading} className="btn btn-primary">
                  {loading ? 'Moving data...' : <><Plus size={18} /> Upload to Aura</>}
                </button>
              </div>
            </div>

            {/* Feed Section */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {feedMode === 'public' ? <Globe size={24} /> : <ShieldCheck size={24} />}
                {feedMode === 'public' ? 'Community Gallery' : 'Personal Vault'}
              </h2>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                {posts.length} {posts.length === 1 ? 'Asset' : 'Assets'}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem' }}>
              <AnimatePresence>
                {posts.map((post, index) => {
                  const isOwner = post.user_id === currentUserId;
                  return (
                    <Motion.div
                      layout
                      key={post.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-card"
                      style={{ overflow: 'hidden', cursor: 'default' }}
                    >
                      <div style={{ height: '180px', overflow: 'hidden', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                        {post.file_type?.startsWith('image') ? (
                          <img src={post.url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="Asset" />
                        ) : (
                          <File size={48} style={{ color: 'var(--text-secondary)' }} />
                        )}
                        {post.is_public && feedMode === 'private' && (
                          <div title="Shared with community" style={{ position: 'absolute', top: '10px', right: '10px', background: 'var(--accent-color)', borderRadius: '50%', padding: '4px', boxShadow: '0 4px 10px rgba(0,0,0,0.3)' }}>
                            <Globe size={12} color="white" />
                          </div>
                        )}
                      </div>
                      <div style={{ padding: '1.2rem' }}>
                        <div style={{ fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.5rem' }}>{post.caption || 'Untitled Asset'}</div>

                        {feedMode === 'public' && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', background: 'rgba(255,255,255,0.04)', padding: '0.4rem 0.6rem', borderRadius: '8px', width: 'fit-content' }}>
                            <UserIcon size={12} />
                            {post.uploader_email}
                          </div>
                        )}

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <span>{new Date(post.created_at).toLocaleDateString()}</span>

                          {/* Owner Actions */}
                          {isOwner && (
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                              {/* Download */}
                              <button
                                onClick={() => handleDownload(post.url, post.file_name)}
                                title="Download Asset"
                                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 0 }}
                              >
                                <Download size={16} />
                              </button>

                              {/* Unshare / Share Toggle */}
                              <button
                                onClick={() => handleVisibilityToggle(post.id, post.is_public)}
                                title={post.is_public ? "Remove from Community" : "Share with Community"}
                                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 0 }}
                              >
                                {post.is_public ? <EyeOff size={16} /> : <Globe size={16} />}
                              </button>

                              {/* Permanent delete is only available from the personal vault */}
                              {feedMode === 'private' ? (
                                <button
                                  onClick={() => handleDelete(post.id)}
                                  title="Delete Permanently"
                                  style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--error)', padding: 0 }}
                                >
                                  <Trash2 size={16} />
                                </button>
                              ) : (
                                <button
                                  onClick={() => handleVisibilityToggle(post.id, post.is_public)}
                                  title="Remove from Community"
                                  style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 0 }}
                                >
                                  <EyeOff size={16} />
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </Motion.div>
                  );
                })}
              </AnimatePresence>
              {posts.length === 0 && (
                <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                  <Folder size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                  <p>{feedMode === 'public' ? 'No community assets shared yet.' : 'Your vault is currently empty.'}</p>
                </div>
              )}
            </div>
          </Motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {notification && (
          <Motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            style={{
              position: 'fixed', bottom: '2rem', right: '2rem',
              padding: '1rem 2rem', borderRadius: '12px', background: notification.type === 'error' ? 'var(--error)' : 'var(--success)',
              color: 'white', fontWeight: 600, boxShadow: '0 10px 25px rgba(0,0,0,0.2)', zIndex: 1000
            }}
          >
            {notification.message}
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
