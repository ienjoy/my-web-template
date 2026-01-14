"""
Unit Tests for Climate Data API

This teaches you:
1. How to write unit tests with pytest
2. Testing API endpoints
3. HTTP status codes and error handling
"""

import pytest
import json
from climate_api import app, df


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestClimateAPI:
    """Test suite for climate API endpoints"""
    
    def test_health_check(self, client):
        """Test that API is running"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'API is running'
    
    def test_get_all_climate(self, client):
        """Test retrieving all climate records"""
        response = client.get('/api/climate')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_climate_by_year(self, client):
        """Test retrieving specific year"""
        response = client.get('/api/climate/2018')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['Year'] == 2018
    
    def test_get_climate_invalid_year(self, client):
        """Test 404 for non-existent year"""
        response = client.get('/api/climate/1900')
        assert response.status_code == 404
    
    def test_get_statistics(self, client):
        """Test statistics endpoint"""
        response = client.get('/api/statistics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'mean' in data
        assert 'min' in data
        assert 'max' in data
        assert 'std' in data
    
    def test_temperature_range(self, client):
        """Test temperature range filtering"""
        response = client.get('/api/climate/range?min_temp=14.8&max_temp=15')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
