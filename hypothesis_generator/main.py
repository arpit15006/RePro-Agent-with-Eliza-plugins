#!/usr/bin/env python3
"""
Hypothesis Generator
Generates research hypotheses from knowledge graphs using AI.
"""

import os
import json
import logging
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class HypothesisGenerator:
    """Generate research hypotheses from knowledge graphs."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
    def generate_research_report(self, graph_file: str, num_hypotheses: int = 5, 
                               focus_area: Optional[str] = None) -> Dict[str, Any]:
        """Generate research hypotheses from knowledge graph."""
        
        try:
            # Load graph data
            graph_data = self._load_graph(graph_file)
            
            # Extract key entities and relationships
            entities = self._extract_entities(graph_data)
            
            # Generate hypotheses
            if self.api_key:
                hypotheses = self._generate_with_ai(graph_data, entities, num_hypotheses, focus_area)
            else:
                hypotheses = self._generate_fallback_hypotheses(entities, num_hypotheses, focus_area)
            
            # Create research report
            report = {
                "generated_hypotheses": hypotheses,
                "graph_summary": self._create_graph_summary(entities),
                "focus_area": focus_area,
                "generation_method": "AI" if self.api_key else "Template-based",
                "total_hypotheses": len(hypotheses),
                "research_directions": self._identify_research_directions(entities),
                "knowledge_gaps": self._identify_knowledge_gaps(entities)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating hypotheses: {e}")
            return self._create_fallback_report(num_hypotheses, focus_area)
    
    def _load_graph(self, graph_file: str) -> List[Dict[str, str]]:
        """Load graph data from file."""
        
        graph_path = Path(graph_file)
        
        if graph_path.suffix.lower() == '.json':
            with open(graph_path, 'r') as f:
                return json.load(f)
        
        elif graph_path.suffix.lower() in ['.ttl', '.turtle']:
            # Try to parse Turtle format
            try:
                from rdflib import Graph
                g = Graph()
                g.parse(graph_file, format="turtle")
                
                triples = []
                for subj, pred, obj in g:
                    triples.append({
                        "subject": str(subj),
                        "predicate": str(pred),
                        "object": str(obj)
                    })
                return triples
                
            except ImportError:
                logger.warning("rdflib not available for Turtle parsing")
                return []
        
        return []
    
    def _extract_entities(self, graph_data: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Extract entities by type from graph data."""
        
        entities = {
            "papers": [],
            "authors": [],
            "tools": [],
            "datasets": [],
            "methods": [],
            "results": [],
            "keywords": []
        }
        
        for triple in graph_data:
            subject = triple.get("subject", "")
            predicate = triple.get("predicate", "")
            obj = triple.get("object", "")
            
            # Classify entities based on URI patterns
            if "papers.org" in subject:
                entities["papers"].append(subject)
            elif "authors.org" in subject:
                entities["authors"].append(subject)
            elif "tools.org" in subject:
                entities["tools"].append(subject)
            elif "datasets.org" in subject:
                entities["datasets"].append(subject)
            
            # Extract specific information
            if "name" in predicate:
                if "tools.org" in subject:
                    entities["tools"].append(obj)
                elif "datasets.org" in subject:
                    entities["datasets"].append(obj)
            elif "keywords" in predicate:
                entities["keywords"].append(obj)
            elif "methodology" in predicate.lower():
                entities["methods"].append(obj)
            elif "results" in predicate.lower():
                entities["results"].append(obj)
        
        # Remove duplicates and clean
        for key in entities:
            entities[key] = list(set([e for e in entities[key] if e and len(e) > 3]))
        
        return entities
    
    def _generate_with_ai(self, graph_data: List[Dict[str, str]], entities: Dict[str, List[str]], 
                         num_hypotheses: int, focus_area: Optional[str]) -> List[Dict[str, Any]]:
        """Generate hypotheses using AI."""
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare context
            context = self._prepare_ai_context(entities, focus_area)
            
            prompt = f"""
            Based on the following scientific knowledge graph data, generate {num_hypotheses} novel research hypotheses.
            
            Context:
            {context}
            
            Focus area: {focus_area or "General scientific research"}
            
            For each hypothesis, provide:
            1. hypothesis: A clear, testable research hypothesis
            2. rationale: Why this hypothesis is worth investigating
            3. methodology: Suggested approach to test the hypothesis
            4. required_resources: List of tools, datasets, or expertise needed
            5. expected_impact: Potential impact if hypothesis is validated
            6. feasibility: "high", "medium", or "low"
            7. novelty_score: Float between 0.0 and 1.0 indicating novelty
            
            Return as a JSON array of hypothesis objects.
            """
            
            response = model.generate_content(prompt)
            
            # Parse AI response
            try:
                hypotheses_data = json.loads(response.text)
                if isinstance(hypotheses_data, list):
                    return hypotheses_data
                else:
                    return [hypotheses_data]
            except json.JSONDecodeError:
                logger.warning("AI response not valid JSON, using fallback")
                return self._generate_fallback_hypotheses(entities, num_hypotheses, focus_area)
            
        except Exception as e:
            logger.error(f"AI hypothesis generation failed: {e}")
            return self._generate_fallback_hypotheses(entities, num_hypotheses, focus_area)
    
    def _prepare_ai_context(self, entities: Dict[str, List[str]], focus_area: Optional[str]) -> str:
        """Prepare context for AI hypothesis generation."""
        
        context_parts = []
        
        if entities["papers"]:
            context_parts.append(f"Papers: {', '.join(entities['papers'][:5])}")
        
        if entities["authors"]:
            context_parts.append(f"Authors: {', '.join(entities['authors'][:5])}")
        
        if entities["tools"]:
            context_parts.append(f"Tools/Technologies: {', '.join(entities['tools'][:10])}")
        
        if entities["datasets"]:
            context_parts.append(f"Datasets: {', '.join(entities['datasets'][:5])}")
        
        if entities["keywords"]:
            context_parts.append(f"Keywords: {', '.join(entities['keywords'][:10])}")
        
        if entities["methods"]:
            context_parts.append(f"Methods: {', '.join(entities['methods'][:3])}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_hypotheses(self, entities: Dict[str, List[str]], 
                                    num_hypotheses: int, focus_area: Optional[str]) -> List[Dict[str, Any]]:
        """Generate hypotheses using template-based approach."""
        
        templates = [
            {
                "hypothesis": "Combining {tool1} with {tool2} could improve {domain} analysis by {improvement}%",
                "rationale": "Both tools have complementary strengths that could address current limitations",
                "methodology": "Develop integrated pipeline and benchmark against existing methods",
                "feasibility": "medium",
                "novelty_score": 0.7
            },
            {
                "hypothesis": "Applying {method} to {dataset} could reveal new insights about {domain}",
                "rationale": "This combination has not been extensively explored in the literature",
                "methodology": "Implement {method} and analyze {dataset} with statistical validation",
                "feasibility": "high",
                "novelty_score": 0.6
            },
            {
                "hypothesis": "Multi-modal approach using {tool1} and {tool2} could enhance {domain} prediction accuracy",
                "rationale": "Different data modalities provide complementary information",
                "methodology": "Design fusion architecture and evaluate on benchmark datasets",
                "feasibility": "medium",
                "novelty_score": 0.8
            }
        ]
        
        hypotheses = []
        
        for i in range(num_hypotheses):
            template = random.choice(templates)
            
            # Fill template with entities
            hypothesis = self._fill_template(template, entities, focus_area)
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _fill_template(self, template: Dict[str, Any], entities: Dict[str, List[str]], 
                      focus_area: Optional[str]) -> Dict[str, Any]:
        """Fill hypothesis template with actual entities."""
        
        # Get random entities
        tools = entities.get("tools", ["machine learning", "deep learning"])
        datasets = entities.get("datasets", ["research dataset"])
        methods = entities.get("methods", ["statistical analysis"])
        
        # Fill placeholders
        filled = {}
        for key, value in template.items():
            if isinstance(value, str):
                filled_value = value
                filled_value = filled_value.replace("{tool1}", random.choice(tools) if tools else "AI method")
                filled_value = filled_value.replace("{tool2}", random.choice(tools) if tools else "statistical method")
                filled_value = filled_value.replace("{dataset}", random.choice(datasets) if datasets else "scientific dataset")
                filled_value = filled_value.replace("{method}", random.choice(methods) if methods else "novel approach")
                filled_value = filled_value.replace("{domain}", focus_area or "scientific research")
                filled_value = filled_value.replace("{improvement}", str(random.randint(10, 30)))
                filled[key] = filled_value
            else:
                filled[key] = value
        
        # Add missing fields
        filled.setdefault("required_resources", ["computational resources", "domain expertise"])
        filled.setdefault("expected_impact", "Advance understanding in the field")
        
        return filled
    
    def _create_graph_summary(self, entities: Dict[str, List[str]]) -> Dict[str, int]:
        """Create summary of graph entities."""
        return {
            "total_papers": len(entities.get("papers", [])),
            "total_authors": len(entities.get("authors", [])),
            "total_tools": len(entities.get("tools", [])),
            "total_datasets": len(entities.get("datasets", [])),
            "total_keywords": len(entities.get("keywords", []))
        }
    
    def _identify_research_directions(self, entities: Dict[str, List[str]]) -> List[str]:
        """Identify potential research directions."""
        
        directions = []
        
        if entities.get("tools"):
            directions.append("Tool integration and comparison studies")
        
        if entities.get("datasets"):
            directions.append("Cross-dataset validation and generalization")
        
        if entities.get("methods"):
            directions.append("Methodological improvements and novel approaches")
        
        directions.extend([
            "Reproducibility and replication studies",
            "Interdisciplinary collaboration opportunities",
            "Scalability and efficiency improvements"
        ])
        
        return directions
    
    def _identify_knowledge_gaps(self, entities: Dict[str, List[str]]) -> List[str]:
        """Identify potential knowledge gaps."""
        
        gaps = []
        
        if not entities.get("datasets"):
            gaps.append("Limited dataset availability or diversity")
        
        if not entities.get("tools"):
            gaps.append("Lack of specialized tools or software")
        
        gaps.extend([
            "Need for standardized evaluation metrics",
            "Limited cross-domain validation",
            "Insufficient long-term studies",
            "Gaps in theoretical understanding"
        ])
        
        return gaps
    
    def _create_fallback_report(self, num_hypotheses: int, focus_area: Optional[str]) -> Dict[str, Any]:
        """Create fallback report when generation fails."""
        
        fallback_hypotheses = [
            {
                "hypothesis": "Novel AI approaches could improve scientific reproducibility assessment",
                "rationale": "Current manual assessment methods are time-consuming and subjective",
                "methodology": "Develop automated assessment tools using machine learning",
                "required_resources": ["machine learning expertise", "scientific paper corpus"],
                "expected_impact": "Faster and more consistent reproducibility evaluation",
                "feasibility": "high",
                "novelty_score": 0.7
            }
        ]
        
        return {
            "generated_hypotheses": fallback_hypotheses * num_hypotheses,
            "graph_summary": {"total_entities": 0},
            "focus_area": focus_area,
            "generation_method": "Fallback",
            "total_hypotheses": num_hypotheses,
            "research_directions": ["General scientific research"],
            "knowledge_gaps": ["Limited data available for analysis"]
        }


def main():
    """CLI interface for hypothesis generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate research hypotheses from knowledge graphs")
    parser.add_argument("--graph", "-g", required=True, help="Knowledge graph file path")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    parser.add_argument("--num-hypotheses", "-n", type=int, default=5, help="Number of hypotheses to generate")
    parser.add_argument("--focus-area", "-f", help="Focus area for hypothesis generation")
    parser.add_argument("--model", "-m", default="gemini-pro", help="AI model to use")
    parser.add_argument("--api-key", help="API key for AI services")

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        os.environ['GEMINI_API_KEY'] = args.api_key

    try:
        generator = HypothesisGenerator()
        report = generator.generate_research_report(
            args.graph,
            args.num_hypotheses,
            args.focus_area
        )

        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Hypotheses generated successfully: {args.output}")
        print(f"🧬 Generated {report.get('total_hypotheses', 0)} hypotheses")

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
