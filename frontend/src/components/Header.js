import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <h1 className="header-title">Restaurant Finder</h1>
        <p className="header-subtitle">Discover your next favorite dining spot with AI-powered recommendations</p>
      </div>
    </header>
  );
};

export default Header;