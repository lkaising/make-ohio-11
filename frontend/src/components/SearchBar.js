import React, { useState, useEffect } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const [city, setCity] = useState('');
  const [priceLevel, setPriceLevel] = useState([]);
  const [cities, setCities] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Fetch available cities when component mounts
    const fetchCities = async () => {
      try {
        const response = await fetch('http://localhost:8000/cities');
        const data = await response.json();
        setCities(data.cities || []);
      } catch (error) {
        console.error('Error fetching cities:', error);
      }
    };

    fetchCities();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch({
        query,
        city: city || null,
        price_levels: priceLevel.length > 0 ? priceLevel : null
      });
    }
  };

  const handlePriceToggle = (level) => {
    if (priceLevel.includes(level)) {
      setPriceLevel(priceLevel.filter(p => p !== level));
    } else {
      setPriceLevel([...priceLevel, level]);
    }
  };

  const exampleQueries = [
    "I want cheap Chinese food that's not too spicy",
    "Looking for a romantic Italian restaurant for date night",
    "Recommend a family-friendly restaurant with good atmosphere",
    "Where can I find authentic ramen?",
    "I need a place with outdoor seating and good cocktails"
  ];

  const handleExampleClick = (example) => {
    setQuery(example);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe what you're looking for..."
            className="search-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? 'Searching...' : 'Find Restaurants'}
          </button>
        </div>

        <div className="examples-container">
          <p className="examples-title">Try an example:</p>
          <div className="example-queries">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                type="button"
                className="example-query"
                onClick={() => handleExampleClick(example)}
                disabled={isLoading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <div className="advanced-search">
          <button 
            type="button" 
            className="advanced-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
            disabled={isLoading}
          >
            {showAdvanced ? '- Hide Advanced Options' : '+ Show Advanced Options'}
          </button>
          
          {showAdvanced && (
            <div className="advanced-options">
              <div className="filter-group">
                <label>City:</label>
                <select 
                  value={city} 
                  onChange={(e) => setCity(e.target.value)}
                  disabled={isLoading}
                >
                  <option value="">All Cities</option>
                  {cities.map((city, index) => (
                    <option key={index} value={city}>{city}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label>Price Level:</label>
                <div className="price-buttons">
                  {[1, 2, 3, 4].map((level) => (
                    <button
                      key={level}
                      type="button"
                      className={`price-button ${priceLevel.includes(level) ? 'active' : ''}`}
                      onClick={() => handlePriceToggle(level)}
                      disabled={isLoading}
                    >
                      {Array(level).fill('$').join('')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar;