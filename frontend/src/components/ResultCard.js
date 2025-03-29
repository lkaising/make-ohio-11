import React from 'react';
import './ResultCard.css';

const ResultCard = ({ results }) => {
  if (!results) {
    return null;
  }

  const { query_analysis, recommendations, error } = results;

  if (error) {
    return (
      <div className="results-error">
        <h3>Error Finding Recommendations</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="no-results">
        <h3>No Recommendations Found</h3>
        <p>Try adjusting your search query or filters.</p>
      </div>
    );
  }

  // Helper function to render stars for ratings
  const renderStars = (rating) => {
    // Extract numeric rating from string like "4.5/5"
    const numericRating = parseFloat(rating.split('/')[0]);
    const maxRating = 5;
    const stars = [];

    for (let i = 1; i <= maxRating; i++) {
      if (i <= numericRating) {
        stars.push(<span key={i} className="star full">★</span>);
      } else if (i - 0.5 <= numericRating) {
        stars.push(<span key={i} className="star half">★</span>);
      } else {
        stars.push(<span key={i} className="star empty">☆</span>);
      }
    }

    return (
      <div className="star-rating">
        {stars} <span className="rating-text">{rating}</span>
      </div>
    );
  };

  return (
    <div className="results-container">
      <div className="recommendations-list">
        {recommendations.map((restaurant, index) => (
          <div key={index} className="restaurant-card">
            <div className="card-badge">{index === 0 ? 'Best Match' : index === 1 ? 'Great Option' : 'Good Alternative'}</div>
            
            <div className="restaurant-header">
              <h3 className="restaurant-name">{restaurant.name}</h3>
              <div className="restaurant-price">{restaurant.price_level}</div>
            </div>
            
            <div className="restaurant-rating">
              {renderStars(restaurant.rating)}
            </div>
            
            <div className="restaurant-tags">
              {restaurant.details.split('.').filter(s => s.trim()).map((detail, i) => {
                // Extract potential tags from the details
                const detailText = detail.trim();
                if (detailText.startsWith('Cuisine:') || 
                    detailText.startsWith('Known for') || 
                    detailText.startsWith('Popular dishes')) {
                  return (
                    <div key={i} className="tag">
                      {detailText}
                    </div>
                  );
                }
                return null;
              }).filter(tag => tag !== null)}
            </div>
            
            <div className="restaurant-address">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              <p>{restaurant.address}</p>
            </div>
            
            <div className="restaurant-match">
              <h4>Why You'll Love It</h4>
              <p>{restaurant.match_reasons}</p>
            </div>
            
            <div className="restaurant-details">
              <h4>Restaurant Details</h4>
              <p>{restaurant.details}</p>
            </div>
            
            <div className="restaurant-actions">
              <a 
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(restaurant.name + ' ' + restaurant.address)}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="map-link"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="3 11 22 2 13 21 11 13 3 11"></polygon>
                </svg>
                View on Map
              </a>
              <button className="bookmark-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                Save
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultCard;