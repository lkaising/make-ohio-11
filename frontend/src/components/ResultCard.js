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

      <h2 className="recommendations-title">Recommended Restaurants</h2>

      <div className="recommendations-list">
        {recommendations.map((restaurant, index) => (
          <div key={index} className="restaurant-card">
            <div className="restaurant-header">
              <h3 className="restaurant-name">{restaurant.name}</h3>
              <div className="restaurant-price">{restaurant.price_level}</div>
            </div>
            
            <div className="restaurant-rating">
              {renderStars(restaurant.rating)}
            </div>
            
            <div className="restaurant-address">
              <strong>Address:</strong> {restaurant.address}
            </div>
            
            <div className="restaurant-match">
              <h4>Why This Matches Your Request</h4>
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
                View on Map
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultCard;