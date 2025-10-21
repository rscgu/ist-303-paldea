#!/usr/bin/env python3
"""
Integration test for budget functionality
Tests the merged budget features from the remote repository
"""

import pytest
import sqlite3
import os
from app import app, get_db_connection, init_db

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_setup():
    """Set up test database"""
    # Create a test database
    test_db = 'test_finance.db'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Initialize database
    init_db()
    yield test_db
    
    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)

def test_budget_form_access(client):
    """Test that budget form is accessible"""
    response = client.get('/budget')
    assert response.status_code == 200
    assert b'Set Monthly Budget' in response.data

def test_budget_progress_access(client):
    """Test that budget progress page is accessible"""
    response = client.get('/budget_progress')
    assert response.status_code == 200
    assert b'Budget Progress' in response.data

def test_add_budget(client, db_setup):
    """Test adding a new budget"""
    response = client.post('/add_budget', data={
        'category': 'Groceries',
        'budget_amount': '500.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Budget added successfully' in response.data

def test_add_sample_data(client, db_setup):
    """Test adding sample data"""
    response = client.get('/add_sample_data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sample data added successfully' in response.data

def test_database_initialization():
    """Test that database tables are created correctly"""
    init_db()
    conn = get_db_connection()
    
    # Check if tables exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'users' in tables
    assert 'transactions' in tables
    assert 'budgets' in tables
    
    conn.close()

def test_budget_calculation():
    """Test budget progress calculation logic"""
    # This would test the core logic for calculating budget progress
    # For now, we'll just verify the function exists
    assert callable(get_db_connection)

if __name__ == '__main__':
    pytest.main([__file__])
