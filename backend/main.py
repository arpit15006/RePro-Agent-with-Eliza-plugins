#!/usr/bin/env python3
"""
RePRO-Agent Backend API
FastAPI server for the RePRO-Agent frontend interface.
"""

import json
import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import our pipeline components
import sys
sys.path.append('..')
sys.path.append('../manuscript_extractor')
sys.path.append('../reproducibility_assistant')
sys.path.append('../knowledge_graph_builder')
sys.path.append('../hypothesis_generator')

from pipeline import ReproAgentPipeline
from manuscript_extractor.main import ManuscriptExtractor
from reproducibility_assistant.main import ReproducibilityAssistant
from knowledge_graph_builder.main import KnowledgeGraphBuilder
from hypothesis_generator.main import HypothesisGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="RePRO-Agent API",
    description="Scientific Reproducibility and Hypothesis Generation API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for processing jobs
processing_jobs: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class PaperAnalysisRequest(BaseModel):
    paper_url: Optional[str] = None
    repo_url: Optional[str] = None
    focus_area: Optional[str] = None
    num_hypotheses: int = 5

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    message: str
    results: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RePRO-Agent API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload-paper")
async def upload_paper(file: UploadFile = File(...)):
    """Upload a paper file for analysis."""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.md', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, MD, and TXT files are supported")
        
        # Create temporary file
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        file_id = str(uuid.uuid4())
        file_path = temp_dir / f"{file_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Uploaded file: {file.filename} -> {file_path}")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "size": len(content),
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-paper")
async def analyze_paper(request: PaperAnalysisRequest, background_tasks: BackgroundTasks):
    """Start paper analysis job."""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        processing_jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Job queued for processing",
            "created_at": datetime.now().isoformat(),
            "request": request.dict()
        }
        
        # Start background processing
        background_tasks.add_task(process_paper_analysis, job_id, request)
        
        return {"job_id": job_id, "status": "pending", "message": "Analysis started"}
        
    except Exception as e:
        logger.error(f"Analysis start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        results=job.get("results")
    )

@app.get("/extract-metadata")
async def extract_metadata(file_path: str):
    """Extract metadata from a paper file."""
    try:
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        extractor = ManuscriptExtractor()
        metadata = extractor.extract_metadata(file_path)
        
        return {"metadata": metadata, "status": "success"}
        
    except Exception as e:
        logger.error(f"Metadata extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assess-reproducibility")
async def assess_reproducibility(repo_url: str):
    """Assess repository reproducibility."""
    try:
        assistant = ReproducibilityAssistant()
        report = assistant.assess_repository(repo_url)
        
        return {"report": report, "status": "success"}
        
    except Exception as e:
        logger.error(f"Reproducibility assessment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-knowledge-graph")
async def build_knowledge_graph(metadata: Dict[str, Any], reproducibility_report: Optional[Dict[str, Any]] = None):
    """Build knowledge graph from metadata and reproducibility report."""
    try:
        builder = KnowledgeGraphBuilder()
        
        # Create temporary files
        temp_dir = Path("temp_graphs")
        temp_dir.mkdir(exist_ok=True)
        
        metadata_file = temp_dir / f"metadata_{uuid.uuid4()}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        reproducibility_file = None
        if reproducibility_report:
            reproducibility_file = temp_dir / f"reproducibility_{uuid.uuid4()}.json"
            with open(reproducibility_file, 'w') as f:
                json.dump(reproducibility_report, f)
        
        # Build graph
        results = builder.load_and_process_files(
            str(metadata_file),
            str(reproducibility_file) if reproducibility_file else None
        )
        
        # Get graph statistics
        stats = builder.get_statistics()
        
        # Serialize graph to JSON-LD for frontend
        graph_data = []
        for subj, pred, obj in builder.graph:
            graph_data.append({
                "subject": str(subj),
                "predicate": str(pred),
                "object": str(obj)
            })
        
        return {
            "graph_data": graph_data,
            "statistics": stats,
            "results": results,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Knowledge graph building error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-hypotheses")
async def generate_hypotheses(graph_data: List[Dict[str, str]], num_hypotheses: int = 5, focus_area: Optional[str] = None):
    """Generate research hypotheses from knowledge graph."""
    try:
        generator = HypothesisGenerator()
        
        # Create temporary graph file
        temp_dir = Path("temp_graphs")
        temp_dir.mkdir(exist_ok=True)
        
        graph_file = temp_dir / f"graph_{uuid.uuid4()}.ttl"
        
        # Reconstruct graph from data
        from rdflib import Graph, URIRef, Literal
        g = Graph()
        for triple in graph_data:
            subj = URIRef(triple["subject"])
            pred = URIRef(triple["predicate"])
            obj = URIRef(triple["object"]) if triple["object"].startswith("http") else Literal(triple["object"])
            g.add((subj, pred, obj))
        
        # Save graph
        g.serialize(destination=str(graph_file), format="turtle")
        
        # Generate hypotheses
        report = generator.generate_research_report(
            str(graph_file),
            num_hypotheses,
            focus_area
        )
        
        return {"report": report, "status": "success"}
        
    except Exception as e:
        logger.error(f"Hypothesis generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-results/{job_id}")
async def download_results(job_id: str):
    """Download analysis results as JSON."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Create downloadable file
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(exist_ok=True)
    
    download_file = temp_dir / f"results_{job_id}.json"
    with open(download_file, 'w') as f:
        json.dump(job["results"], f, indent=2)
    
    return FileResponse(
        path=str(download_file),
        filename=f"repro_agent_results_{job_id}.json",
        media_type="application/json"
    )

async def process_paper_analysis(job_id: str, request: PaperAnalysisRequest):
    """Background task to process paper analysis."""
    try:
        job = processing_jobs[job_id]
        job["status"] = "processing"
        job["progress"] = 10
        job["message"] = "Starting analysis..."
        
        # Create output directory
        output_dir = Path(f"analysis_results/{job_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipeline
        pipeline = ReproAgentPipeline(work_dir=str(output_dir))
        
        # Update progress
        job["progress"] = 30
        job["message"] = "Processing paper and repository..."
        
        # Run pipeline
        results = pipeline.run_complete_pipeline(
            paper_path=request.paper_url,
            repo_url=request.repo_url,
            num_hypotheses=request.num_hypotheses,
            focus_area=request.focus_area,
            model="gemini-pro"
        )
        
        # Update progress
        job["progress"] = 80
        job["message"] = "Finalizing results..."
        
        # Load and structure results
        structured_results = {}
        
        # Load metadata
        if "metadata_file" in results and Path(results["metadata_file"]).exists():
            with open(results["metadata_file"], 'r') as f:
                structured_results["metadata"] = json.load(f)
        
        # Load reproducibility report
        if "reproducibility_file" in results and Path(results["reproducibility_file"]).exists():
            with open(results["reproducibility_file"], 'r') as f:
                structured_results["reproducibility"] = json.load(f)
        
        # Load hypotheses
        if "hypotheses_file" in results and Path(results["hypotheses_file"]).exists():
            with open(results["hypotheses_file"], 'r') as f:
                structured_results["hypotheses"] = json.load(f)

        # Load graph data
        if "graph_file" in results and Path(results["graph_file"]).exists():
            try:
                # Load the knowledge graph and convert to frontend format
                from knowledge_graph_builder.main import KnowledgeGraphBuilder
                builder = KnowledgeGraphBuilder()

                # Load the graph file
                if results["graph_file"].endswith('.ttl'):
                    # Parse Turtle format
                    try:
                        from rdflib import Graph
                        g = Graph()
                        g.parse(results["graph_file"], format="turtle")

                        graph_data = []
                        for subj, pred, obj in g:
                            graph_data.append({
                                "subject": str(subj),
                                "predicate": str(pred),
                                "object": str(obj)
                            })
                        structured_results["graph_data"] = graph_data

                    except ImportError:
                        logger.warning("rdflib not available for graph parsing")
                        structured_results["graph_data"] = []
                else:
                    # Try to load as JSON
                    try:
                        with open(results["graph_file"], 'r') as f:
                            structured_results["graph_data"] = json.load(f)
                    except:
                        structured_results["graph_data"] = []

            except Exception as e:
                logger.warning(f"Could not load graph data: {e}")
                structured_results["graph_data"] = []

        # Complete job
        job["status"] = "completed"
        job["progress"] = 100
        job["message"] = "Analysis completed successfully"
        job["results"] = structured_results
        job["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"Processing error for job {job_id}: {e}")
        job["status"] = "failed"
        job["progress"] = 0
        job["message"] = f"Analysis failed: {str(e)}"
        job["error"] = str(e)

# Mount static files for frontend (optional)
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# Serve frontend
@app.get("/app/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the frontend application."""
    frontend_path = Path("frontend/dist/index.html")
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not built")

if __name__ == "__main__":
    # Create necessary directories
    Path("temp_uploads").mkdir(exist_ok=True)
    Path("temp_graphs").mkdir(exist_ok=True)
    Path("temp_downloads").mkdir(exist_ok=True)
    Path("analysis_results").mkdir(exist_ok=True)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
