import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Menu, X, LayoutDashboard, UploadCloud, User, LogOut, 
  Activity, Bell, ChevronDown, CheckCircle, AlertOctagon, FileText
} from 'lucide-react';
import axios from 'axios';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [isOpen, setIsOpen] = useState(false); // Mobile menu
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [isConnected, setIsConnected] = useState(true); // Mock health status
  const [unreadCount, setUnreadCount] = useState(0);

  const profileMenuRef = useRef(null);

  // Close profile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  // Mock Fetch Health & Unread Anomalies
  useEffect(() => {
    if (isAuthenticated) {
        // Here we would fetch from /api/health and /api/results
        // For now, mock it
        const checkStatus = async () => {
            try {
               // const health = await axios.get('/api/health');
               // setIsConnected(health.status === 200);
               setIsConnected(true);
            } catch (e) { setIsConnected(false); }
        };
        const fetchUnread = async () => {
             // Mock fetch
             // Mock fetch or remove
             setUnreadCount(0); 
        };
        checkStatus();
        fetchUnread();
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const NavLink = ({ to, children, icon: Icon, badge }) => {
    const isActive = location.pathname === to;
    return (
      <Link 
        to={to} 
        className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
          isActive 
            ? 'bg-gradient-to-r from-[var(--primary-start)] to-[var(--primary-end)] text-white shadow-md' 
            : 'text-gray-300 hover:text-white hover:bg-white/5'
        }`}
      >
        {Icon && <Icon className={`w-4 h-4 mr-2 ${isActive ? 'text-white' : 'text-gray-400'}`} />}
        {children}
        {badge > 0 && (
            <span className="ml-2 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">
                {badge}
            </span>
        )}
      </Link>
    );
  };

  const MobileNavLink = ({ to, children, icon: Icon, onClick }) => {
     const isActive = location.pathname === to;
     return (
        <Link
            to={to}
            onClick={onClick}
            className={`flex items-center w-full px-4 py-3 rounded-md text-base font-medium ${
                 isActive 
                    ? 'bg-indigo-600/20 text-indigo-400 border-l-4 border-indigo-500' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
            }`}
        >
             {Icon && <Icon className="w-5 h-5 mr-3" />}
             {children}
        </Link>
     );
  };

  return (
    <nav className="bg-[var(--bg)] border-b border-[var(--card)] sticky top-0 z-50 backdrop-blur-md bg-opacity-80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center space-x-2 group">
              <div className="bg-gradient-to-br from-[var(--primary-start)] to-[var(--primary-end)] p-2 rounded-lg shadow-lg group-hover:shadow-emerald-500/20 transition-all">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-xl tracking-tight text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-indigo-400 group-hover:to-cyan-400 transition-all">
                Anamoly<span className="text-gray-500 font-light">CNS</span>
              </span>
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex ml-10 space-x-2">
                {isAuthenticated ? (
                    <>
                        <NavLink to="/dashboard" icon={LayoutDashboard}>Dashboard</NavLink>
                        <NavLink to="/upload" icon={UploadCloud}>Upload</NavLink>
                        <NavLink to="/results" icon={FileText} badge={unreadCount}>Results</NavLink>
                    </>
                ) : (
                    <NavLink to="/" icon={Activity}>Home</NavLink>
                )}
            </div>
          </div>

          {/* Right Side: Status & Profile/Auth */}
          <div className="hidden md:flex items-center space-x-4">
             {/* System Status Chip */}
             <div className={`hidden lg:flex items-center pl-3 pr-4 py-1 rounded-full text-xs font-medium border ${
                 isConnected ? 'border-green-500/20 bg-green-500/10 text-green-400' : 'border-red-500/20 bg-red-500/10 text-red-400'
             }`}>
                 <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                 {isConnected ? 'System Online' : 'System Offline'}
             </div>

             {isAuthenticated ? (
                 <div className="relative ml-3" ref={profileMenuRef}>
                    <button 
                        onClick={() => setShowProfileMenu(!showProfileMenu)}
                        className="flex items-center space-x-3 text-sm focus:outline-none hover:opacity-80 transition-opacity"
                    >
                        <div className="flex flex-col items-end hidden lg:flex">
                            <span className="text-white font-medium">{user?.name || 'User'}</span>
                            <span className="text-gray-500 text-xs">{user?.email}</span>
                        </div>
                        <div className="h-9 w-9 rounded-full bg-gradient-to-r from-gray-700 to-gray-600 flex items-center justify-center text-white ring-2 ring-[var(--card)] shadow-lg">
                           {user?.avatar ? (
                               <img src={user.avatar} alt="User" className="h-9 w-9 rounded-full object-cover" />
                           ) : (
                               <span className="font-bold text-xs">{user?.name?.charAt(0) || 'U'}</span>
                           )}
                        </div>
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                    </button>

                    {/* Dropdown Menu */}
                    {showProfileMenu && (
                        <div className="absolute right-0 mt-2 w-48 rounded-xl bg-[var(--card)] border border-white/5 shadow-2xl py-1 ring-1 ring-black ring-opacity-5 animate-fade origin-top-right">
                             <div className="px-4 py-3 border-b border-white/5 lg:hidden">
                                <p className="text-sm text-white font-medium">{user?.name}</p>
                                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                             </div>
                             <Link 
                                to="/profile" 
                                className="block px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white flex items-center"
                                onClick={() => setShowProfileMenu(false)}
                            >
                                <User className="w-4 h-4 mr-2" /> Profile
                             </Link>
                             <button
                                onClick={() => { handleLogout(); setShowProfileMenu(false); }}
                                className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 flex items-center"
                             >
                                <LogOut className="w-4 h-4 mr-2" /> Logout
                             </button>
                        </div>
                    )}
                 </div>
             ) : (
                 <div className="flex items-center space-x-3">
                     <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors">Log in</Link>
                     <Link to="/signup" className="btn-primary text-sm shadow-sm hover:shadow-cyan-500/20">
                        Sign up
                     </Link>
                 </div>
             )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/10 focus:outline-none"
            >
              {isOpen ? <X className="block h-6 w-6" /> : <Menu className="block h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-[var(--card)] border-b border-white/5 animate-fade">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
             {isAuthenticated ? (
                 <>
                    <MobileNavLink to="/dashboard" icon={LayoutDashboard}>Dashboard</MobileNavLink>
                    <MobileNavLink to="/upload" icon={UploadCloud}>Upload</MobileNavLink>
                    <MobileNavLink to="/results" icon={FileText}>Results {unreadCount > 0 && `(${unreadCount})`}</MobileNavLink>
                    <MobileNavLink to="/profile" icon={User}>Profile</MobileNavLink>
                    <div className="border-t border-white/5 mt-4 pt-4 pb-2">
                        <div className="flex items-center px-4 mb-3">
                             <div className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center text-white">
                                {user?.name?.charAt(0) || 'U'}
                             </div>
                             <div className="ml-3">
                                 <div className="text-base font-medium text-white">{user?.name}</div>
                                 <div className="text-xs font-medium text-gray-500">{user?.email}</div>
                             </div>
                        </div>
                        <button 
                            onClick={handleLogout}
                            className="w-full flex items-center px-4 py-3 text-base font-medium text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-md"
                        >
                            <LogOut className="w-5 h-5 mr-3" /> Logout
                        </button>
                    </div>
                 </>
             ) : (
                 <>
                    <MobileNavLink to="/" icon={Activity}>Home</MobileNavLink>
                    <div className="border-t border-white/5 mt-4 pt-4 flex flex-col space-y-2 px-2">
                         <Link to="/login" className="block w-full text-center px-4 py-2 text-gray-300 border border-gray-600 rounded-md hover:bg-white/5">Log in</Link>
                         <Link to="/signup" className="block w-full text-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-cyan-500 text-white rounded-md font-medium">Sign up</Link>
                    </div>
                 </>
             )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
