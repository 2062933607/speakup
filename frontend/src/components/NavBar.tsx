import { NavLink, useLocation } from 'react-router-dom';
import './NavBar.css';

const tabs = [
  { to: '/', label: 'Home', icon: '🏠' },
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/history', label: 'History', icon: '📋' },
];

export default function NavBar() {
  const location = useLocation();

  // 对话页面不显示导航栏
  if (location.pathname.startsWith('/chat/')) {
    return null;
  }

  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.to === '/'}
          className={({ isActive }) =>
            `nav-item ${isActive ? 'active' : ''}`
          }
        >
          <span className="nav-icon">{tab.icon}</span>
          <span className="nav-label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
