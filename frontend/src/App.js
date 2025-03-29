import React, { useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (searchParams) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchParams.query,
          num_results: 3,
          city: searchParams.city,
          price_levels: searchParams.price_levels
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to fetch recommendations. Please make sure the backend server is running.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      
      <main className="content">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} hasResults={results !== null} />
        
        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Finding the perfect restaurants for you...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {!isLoading && !error && results && (
          <ResultCard results={results} />
        )}
        
        {!isLoading && !error && !results && (
          <div className="welcome-container">
            <h2>Welcome to Restaurant Finder!</h2>
            <p>Describe what you're looking for, and our AI will recommend the perfect restaurant options.</p>
            <div className="features">
              <div className="feature">
                <h3>Natural Language Search</h3>
                <p>Search for restaurants the way you'd ask a friend for recommendations.</p>
              </div>
              <div className="feature">
                <h3>AI-Powered Matching</h3>
                <p>Our system understands your preferences and matches them to the best restaurants.</p>
              </div>
              <div className="feature">
                <h3>Growing Database</h3>
                <p>Starting with Columbus, with more cities coming soon!</p>
              </div>
            </div>
          </div>
        )}
      </main>
      
      <footer className="footer">
        <p>Restaurant Finder - Hackathon Project © 2025</p>
      </footer>
    </div>
  );
}

export default App;