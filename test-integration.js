#!/usr/bin/env node

/**
 * Integration test to verify all services are running correctly
 */

import axios from 'axios';

console.log('🔬 RePRO-Agent Integration Test');
console.log('===============================\n');

async function testBackendHealth() {
    try {
        console.log('1. Testing Backend Health...');
        const response = await axios.get('http://localhost:8000/health');
        console.log('   ✅ Backend is healthy:', response.data);
        return true;
    } catch (error) {
        console.log('   ❌ Backend not accessible:', error.message);
        return false;
    }
}

async function testFrontend() {
    try {
        console.log('2. Testing Frontend...');
        const response = await axios.get('http://localhost:5173/', { timeout: 5000 });
        console.log('   ✅ Frontend is accessible (status:', response.status, ')');
        return true;
    } catch (error) {
        console.log('   ❌ Frontend not accessible:', error.message);
        return false;
    }
}

async function testManuscriptAnalysis() {
    try {
        console.log('3. Testing Manuscript Analysis API...');
        
        // Test with a sample paper
        const analysisResponse = await axios.post('http://localhost:8000/analyze-paper', {
            paper_url: 'temp_uploads/5639b493-9bb2-4397-8383-1585170fbd6a_test_paper.md',
            focus_area: 'integration test',
            num_hypotheses: 2
        });
        
        console.log('   ✅ Analysis started:', analysisResponse.data);
        
        const jobId = analysisResponse.data.job_id;
        
        // Wait a moment and check status
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const statusResponse = await axios.get(`http://localhost:8000/job-status/${jobId}`);
        console.log('   ✅ Job status:', statusResponse.data.status);
        
        return true;
    } catch (error) {
        console.log('   ❌ Manuscript analysis failed:', error.message);
        return false;
    }
}

async function testElizaPlugin() {
    try {
        console.log('4. Testing Eliza Plugin Structure...');
        
        // Check if plugin files exist
        const fs = await import('fs');
        const path = await import('path');
        
        const pluginPath = './manuscript-extractor-plugin';
        const requiredFiles = [
            'package.json',
            'src/index.ts',
            'src/plugin.ts',
            'dist/src/index.js'
        ];
        
        let allFilesExist = true;
        for (const file of requiredFiles) {
            const filePath = path.join(pluginPath, file);
            if (fs.existsSync(filePath)) {
                console.log(`   ✅ ${file} exists`);
            } else {
                console.log(`   ❌ ${file} missing`);
                allFilesExist = false;
            }
        }
        
        return allFilesExist;
    } catch (error) {
        console.log('   ❌ Plugin structure check failed:', error.message);
        return false;
    }
}

async function runIntegrationTest() {
    console.log('Starting comprehensive integration test...\n');
    
    const results = {
        backend: await testBackendHealth(),
        frontend: await testFrontend(),
        analysis: await testManuscriptAnalysis(),
        plugin: await testElizaPlugin()
    };
    
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    
    Object.entries(results).forEach(([test, passed]) => {
        const status = passed ? '✅ PASS' : '❌ FAIL';
        console.log(`${test.padEnd(12)}: ${status}`);
    });
    
    const allPassed = Object.values(results).every(result => result);
    
    console.log('\n🎯 Overall Status:');
    if (allPassed) {
        console.log('✅ ALL SYSTEMS OPERATIONAL!');
        console.log('🚀 Your RePRO-Agent + Eliza Plugin is ready for the hackathon!');
        console.log('\n💬 Try these commands:');
        console.log('   • Frontend: http://localhost:5173/');
        console.log('   • Backend API: http://localhost:8000/docs');
        console.log('   • Plugin: cd manuscript-extractor-plugin && npm start');
    } else {
        console.log('⚠️  Some components need attention');
        console.log('   Check the failed tests above and ensure all services are running');
    }
    
    return allPassed;
}

// Run the test
runIntegrationTest().catch(console.error);
