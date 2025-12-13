import { useAuth } from '../context/AuthContext';
import { User, Mail, Shield, Calendar } from 'lucide-react';

const Profile = () => {
  const { user, loading } = useAuth();
  
  if (loading) return <div className="text-center text-white mt-10 animate-pulse">Loading profile...</div>;
  
  if (!user) return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center mt-10">
        <div className="bg-[var(--card)] p-8 rounded-xl shadow-lg border border-red-500/20">
            <h2 className="text-xl font-bold text-white mb-2">Profile Unavailable</h2>
            <p className="text-gray-400 mb-6">Unable to load user data. Please try logging in again.</p>
            <button className="btn-primary" onClick={() => window.location.href = '/login'}>Go to Login</button>
        </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white mb-8">User Profile</h1>
      
      <div className="bg-[var(--card)] rounded-2xl shadow-xl border border-white/5 overflow-hidden">
        {/* Header/Banner */}
        <div className="h-32 bg-gradient-to-r from-[var(--primary-start)] to-[var(--primary-end)] relative">
            <div className="absolute -bottom-10 left-8">
                <div className="h-24 w-24 rounded-full bg-gray-900 border-4 border-[var(--card)] flex items-center justify-center text-white text-3xl font-bold">
                    {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </div>
            </div>
        </div>
        
        <div className="pt-14 pb-8 px-8">
            <h2 className="text-2xl font-bold text-white">{user.name || 'Anonymous User'}</h2>
            <p className="text-gray-400">{user.email}</p>
            <div className="flex items-center gap-2 mt-2">
                 <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Free Tier
                 </span>
                 <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-300 border border-green-500/30">
                    Active
                 </span>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex items-center mb-2 text-gray-400">
                        <Mail className="w-4 h-4 mr-2" /> Email Address
                    </div>
                    <div className="text-white font-medium">{user.email}</div>
                </div>

                <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex items-center mb-2 text-gray-400">
                        <Shield className="w-4 h-4 mr-2" /> Account ID
                    </div>
                    <div className="text-white font-medium font-mono text-sm opacity-80">
                        {user.id || 'N/A'}
                    </div>
                </div>
                
                 <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                    <div className="flex items-center mb-2 text-gray-400">
                        <Calendar className="w-4 h-4 mr-2" /> Member Since
                    </div>
                    <div className="text-white font-medium">
                        {new Date().toLocaleDateString()} {/* Mock date */}
                    </div>
                </div>
            </div>
            
            <div className="mt-8 flex justify-end">
                <button className="btn-secondary mr-3">Edit Profile</button>
                <button className="btn-primary">Upgrade Plan</button>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
