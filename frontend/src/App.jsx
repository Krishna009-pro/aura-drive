import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LogOut, Upload, Trash2, Folder, ShieldCheck, Mail, Lock, Plus, File } from 'lucide-react';
import { authApi, driveApi } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('aura_token'));
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  
  // Auth state
  const [authMode, setAuthMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [caption, setCaption] = useState('');

  useEffect(() => {
    if (token) {
      loadFeed();
    }
  }, [token]);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const loadFeed = async () => {
    try {
      const res = await driveApi.getFeed();
      setPosts(res.data.posts || []);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) logout();
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (authMode === 'login') {
        const res = await authApi.login(email, password);
        localStorage.setItem('aura_token', res.data.access_token);
        setToken(res.data.access_token);
        showNotification('Welcome to Aura Drive');
      } else {
        await authApi.register(email, password);
        showNotification('Registration successful! Please login.');
        setAuthMode('login');
      }
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Authentication failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('aura_token');
    setToken(null);
    setPosts([]);
  };

  const handleUpload = async () => {
    if (!uploadFile) return showNotification('Please select a file', 'error');
    try {
      setLoading(true);
      await driveApi.upload(uploadFile, caption);
      showNotification('Asset stored securely');
      setUploadFile(null);
      setCaption('');
      loadFeed();
    } catch (err) {
      showNotification('Upload failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this asset permanently?')) return;
    try {
      await driveApi.deletePost(id);
      showNotification('Asset removed');
      loadFeed();
    } catch (err) {
      showNotification('Delete failed', 'error');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem 2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 0', marginBottom: '2rem' }}>
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          style={{ fontSize: '1.6rem', fontWeight: 700, background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          AURA DRIVE
        </motion.div>
        {token && (
          <button onClick={logout} className="btn" style={{ color: 'var(--text-secondary)' }}>
            <LogOut size={18} /> Sign Out
          </button>
        )}
      </header>

      <AnimatePresence mode="wait">
        {!token ? (
          <motion.div 
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
                  {authMode === mode && <motion.div layoutId="underline" style={{ position: 'absolute', bottom: -5, left: 0, width: '100%', height: '3px', background: 'var(--accent-color)', borderRadius: '4px' }} />}
                </span>
              ))}
            </div>

            <form onSubmit={handleAuth}>
              <div style={{ marginBottom: '1.2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.6rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Email Address</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                  <input 
                    type="email" 
                    className="input-field" 
                    value={email} 
                    onChange={e => setEmail(e.target.value)} 
                    placeholder="name@company.com" 
                    required 
                    style={{ paddingLeft: '3rem' }}
                  />
                </div>
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.6rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Password</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                  <input 
                    type="password" 
                    className="input-field" 
                    value={password} 
                    onChange={e => setPassword(e.target.value)} 
                    placeholder="••••••••" 
                    required 
                    style={{ paddingLeft: '3rem' }}
                  />
                </div>
              </div>
              <button disabled={loading} className="btn btn-primary" style={{ width: '100%' }}>
                {loading ? 'Processing...' : 'Continue'}
              </button>
            </form>
          </motion.div>
        ) : (
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="glass-card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', padding: '2rem', marginBottom: '3rem' }}>
              <div>
                <h2 style={{ marginBottom: '0.5rem' }}>Cloud Deposit</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Securely upload and manage your premium assets.</p>
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
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="Asset caption..." 
                  value={caption} 
                  onChange={e => setCaption(e.target.value)}
                />
                <button onClick={handleUpload} disabled={loading} className="btn btn-primary">
                  {loading ? 'Moving data...' : <><Plus size={18} /> Upload to Aura</>}
                </button>
              </div>
            </div>

            <h2 style={{ marginBottom: '1.5rem' }}>Secure Assets</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem' }}>
              <AnimatePresence>
                {posts.map((post, index) => (
                  <motion.div 
                    layout
                    key={post.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ delay: index * 0.05 }}
                    className="glass-card"
                    style={{ overflow: 'hidden', cursor: 'default' }}
                  >
                    <div style={{ height: '180px', overflow: 'hidden', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {post.file_type?.startsWith('image') ? (
                        <img src={post.url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="Asset" />
                      ) : (
                        <File size={48} style={{ color: 'var(--text-secondary)' }} />
                      )}
                    </div>
                    <div style={{ padding: '1.2rem' }}>
                      <div style={{ fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.5rem' }}>{post.caption || 'Untitled Asset'}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <span>{new Date(post.created_at).toLocaleDateString()}</span>
                        <Trash2 
                          size={16} 
                          onClick={() => handleDelete(post.id)}
                          style={{ cursor: 'pointer', color: 'var(--error)', transition: 'transform 0.2s' }} 
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {posts.length === 0 && (
                <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                  <Folder size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                  <p>Your vault is currently empty.</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {notification && (
          <motion.div 
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
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
