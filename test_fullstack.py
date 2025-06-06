#!/usr/bin/env python3
"""
Full-Stack Test for RePRO-Agent
Tests the complete pipeline including backend API and frontend integration.
"""

import json
import logging
import requests
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
API_BASE = "http://localhost:8000"

def test_api_health():
    """Test API health check."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ API Health Check: {data['status']}")
        return True
    except Exception as e:
        logger.error(f"❌ API Health Check Failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality."""
    try:
        # Create a test file
        test_content = """# Test Scientific Paper

## Abstract
This is a test paper for the RePRO-Agent system.

## Introduction
Testing the manuscript extraction capabilities.

## Methods
We used Python and machine learning.

## Results
The system works correctly.

## Conclusions
This test validates the upload functionality.
"""
        
        test_file = Path("test_paper.md")
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Upload the file
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE}/upload-paper", files=files, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"✅ File Upload: {data['filename']} ({data['size']} bytes)")
        
        # Cleanup
        test_file.unlink()
        
        return data['file_path']
        
    except Exception as e:
        logger.error(f"❌ File Upload Failed: {e}")
        return None

def test_analysis_pipeline(file_path):
    """Test the complete analysis pipeline."""
    try:
        # Start analysis
        analysis_request = {
            "paper_url": file_path,
            "repo_url": "https://github.com/pytorch/pytorch",
            "focus_area": "machine learning",
            "num_hypotheses": 3
        }
        
        response = requests.post(f"{API_BASE}/analyze-paper", json=analysis_request, timeout=30)
        response.raise_for_status()
        job_data = response.json()
        
        job_id = job_data['job_id']
        logger.info(f"✅ Analysis Started: Job ID {job_id}")
        
        # Poll for completion (with timeout)
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{API_BASE}/job-status/{job_id}", timeout=10)
            response.raise_for_status()
            status_data = response.json()
            
            logger.info(f"📊 Analysis Progress: {status_data['progress']}% - {status_data['message']}")
            
            if status_data['status'] == 'completed':
                logger.info("✅ Analysis Completed Successfully")
                return status_data
            elif status_data['status'] == 'failed':
                logger.error(f"❌ Analysis Failed: {status_data['message']}")
                return None
            
            time.sleep(5)  # Wait 5 seconds before next check
        
        logger.error("❌ Analysis Timeout")
        return None
        
    except Exception as e:
        logger.error(f"❌ Analysis Pipeline Failed: {e}")
        return None

def test_individual_endpoints():
    """Test individual API endpoints."""
    try:
        # Test metadata extraction
        logger.info("🧪 Testing metadata extraction...")
        response = requests.get(f"{API_BASE}/extract-metadata", 
                              params={"file_path": "sample_paper.md"}, 
                              timeout=30)
        if response.status_code == 200:
            logger.info("✅ Metadata extraction endpoint working")
        else:
            logger.warning(f"⚠️ Metadata extraction returned {response.status_code}")
        
        # Test reproducibility assessment
        logger.info("🧪 Testing reproducibility assessment...")
        response = requests.get(f"{API_BASE}/assess-reproducibility", 
                              params={"repo_url": "https://github.com/pytorch/pytorch"}, 
                              timeout=60)
        if response.status_code == 200:
            logger.info("✅ Reproducibility assessment endpoint working")
        else:
            logger.warning(f"⚠️ Reproducibility assessment returned {response.status_code}")
        
        # Test knowledge graph building
        logger.info("🧪 Testing knowledge graph building...")
        sample_metadata = {
            "title": "Test Paper",
            "author": ["Test Author"],
            "abstract": "Test abstract"
        }
        response = requests.post(f"{API_BASE}/build-knowledge-graph", 
                               json={"metadata": sample_metadata}, 
                               timeout=30)
        if response.status_code == 200:
            logger.info("✅ Knowledge graph building endpoint working")
        else:
            logger.warning(f"⚠️ Knowledge graph building returned {response.status_code}")
        
        # Test hypothesis generation
        logger.info("🧪 Testing hypothesis generation...")
        sample_graph_data = [
            {
                "subject": "https://papers.org/test",
                "predicate": "https://schema.org/name",
                "object": "Test Paper"
            }
        ]
        response = requests.post(f"{API_BASE}/generate-hypotheses", 
                               json={"graph_data": sample_graph_data}, 
                               timeout=30)
        if response.status_code == 200:
            logger.info("✅ Hypothesis generation endpoint working")
        else:
            logger.warning(f"⚠️ Hypothesis generation returned {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Individual endpoint testing failed: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible."""
    try:
        response = requests.get("http://localhost:5173", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Frontend accessible at http://localhost:5173")
            return True
        else:
            logger.error(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Frontend not accessible: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🧬 RePRO-Agent Full-Stack Test Suite")
    logger.info("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: API Health
    logger.info("\n🧪 Test 1: API Health Check")
    if test_api_health():
        tests_passed += 1
    
    # Test 2: Frontend Accessibility
    logger.info("\n🧪 Test 2: Frontend Accessibility")
    if test_frontend_accessibility():
        tests_passed += 1
    
    # Test 3: File Upload
    logger.info("\n🧪 Test 3: File Upload")
    file_path = test_file_upload()
    if file_path:
        tests_passed += 1
    
    # Test 4: Individual Endpoints
    logger.info("\n🧪 Test 4: Individual API Endpoints")
    if test_individual_endpoints():
        tests_passed += 1
    
    # Test 5: Complete Analysis Pipeline (only if file upload worked)
    logger.info("\n🧪 Test 5: Complete Analysis Pipeline")
    if file_path:
        result = test_analysis_pipeline(file_path)
        if result:
            tests_passed += 1
            
            # Display sample results
            if result.get('results'):
                logger.info("\n📊 Sample Analysis Results:")
                if 'metadata' in result['results']:
                    logger.info(f"  📄 Paper Title: {result['results']['metadata'].get('title', 'N/A')}")
                if 'reproducibility' in result['results']:
                    score = result['results']['reproducibility'].get('reproducibility_score', 0)
                    logger.info(f"  🔍 Reproducibility Score: {score:.2f}")
                if 'hypotheses' in result['results']:
                    hypotheses = result['results']['hypotheses'].get('generated_hypotheses', [])
                    logger.info(f"  🧬 Generated Hypotheses: {len(hypotheses)}")
    else:
        logger.warning("⚠️ Skipping pipeline test due to upload failure")
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info(f"🏁 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        logger.info("🎉 All tests passed! RePRO-Agent is working correctly.")
        logger.info("\n🌐 Access the application:")
        logger.info("  Frontend: http://localhost:5173")
        logger.info("  Backend:  http://localhost:8000")
        logger.info("  API Docs: http://localhost:8000/docs")
        return True
    else:
        logger.error(f"❌ {total_tests - tests_passed} tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
