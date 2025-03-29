import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <h1 className="header-title">Restaurant Finder</h1>
        <p className="header-subtitle">Find the perfect dining spot with natural language search</p>
      </div>
    </header>
  );
};

export default Header;