#!/usr/bin/env python3
"""
Hypothesis Generator Plugin for Eliza
Generates novel research hypotheses using knowledge graph analysis and LLM reasoning.
"""

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import networkx as nx
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define namespaces
SCHEMA = Namespace("https://schema.org/")
REPRO = Namespace("https://reproducibility.org/")
SCIENTIFIC = Namespace("https://scientific.org/")


class HypothesisGenerator:
    """Generate research hypotheses from knowledge graphs."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """Initialize the hypothesis generator."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.graph = Graph()
        self.nx_graph = nx.Graph()
        
        if not self.api_key:
            logger.warning("No API key provided. Hypothesis generation will be limited.")
    
    def load_knowledge_graph(self, graph_file: str):
        """Load RDF knowledge graph from file."""
        try:
            self.graph.parse(graph_file)
            logger.info(f"Loaded knowledge graph with {len(self.graph)} triples")
            self._build_networkx_graph()
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
            raise
    
    def _build_networkx_graph(self):
        """Build NetworkX graph for network analysis."""
        for subj, pred, obj in self.graph:
            if isinstance(obj, URIRef):  # Only add URI-to-URI relationships
                self.nx_graph.add_edge(str(subj), str(obj), predicate=str(pred))
    
    def analyze_graph_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the knowledge graph."""
        analysis = {
            "entity_counts": defaultdict(int),
            "relationship_counts": defaultdict(int),
            "tool_usage": defaultdict(int),
            "dataset_usage": defaultdict(int),
            "author_collaborations": defaultdict(int),
            "reproducibility_scores": [],
            "highly_connected_entities": [],
            "research_gaps": []
        }
        
        # Count entity types
        for subj, pred, obj in self.graph:
            if pred == RDF.type:
                analysis["entity_counts"][str(obj)] += 1
            else:
                analysis["relationship_counts"][str(pred)] += 1
        
        # Analyze tool usage
        for subj, pred, obj in self.graph:
            if pred == SCIENTIFIC.usesTool:
                tool_name = self._get_entity_name(obj)
                if tool_name:
                    analysis["tool_usage"][tool_name] += 1
        
        # Analyze dataset usage
        for subj, pred, obj in self.graph:
            if pred == SCIENTIFIC.usesDataset:
                dataset_name = self._get_entity_name(obj)
                if dataset_name:
                    analysis["dataset_usage"][dataset_name] += 1
        
        # Collect reproducibility scores
        for subj, pred, obj in self.graph:
            if pred == REPRO.reproducibilityScore:
                try:
                    score = float(obj)
                    analysis["reproducibility_scores"].append(score)
                except ValueError:
                    pass
        
        # Find highly connected entities using NetworkX
        if self.nx_graph.nodes():
            centrality = nx.degree_centrality(self.nx_graph)
            top_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            analysis["highly_connected_entities"] = top_entities
        
        return analysis
    
    def _get_entity_name(self, entity_uri: URIRef) -> Optional[str]:
        """Get the name of an entity from the graph."""
        for pred in [SCHEMA.name, RDFS.label]:
            for name in self.graph.objects(entity_uri, pred):
                return str(name)
        return None
    
    def find_research_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify research opportunities from graph analysis."""
        opportunities = []
        
        # Tool combination opportunities
        popular_tools = dict(analysis["tool_usage"].most_common(10))
        for i, tool1 in enumerate(popular_tools.keys()):
            for tool2 in list(popular_tools.keys())[i+1:]:
                # Check if tools are rarely used together
                combined_usage = self._count_combined_tool_usage(tool1, tool2)
                if combined_usage == 0:
                    opportunities.append({
                        "type": "tool_combination",
                        "description": f"Explore combining {tool1} with {tool2}",
                        "tools": [tool1, tool2],
                        "rationale": "These popular tools haven't been used together in existing research"
                    })
        
        # Dataset reuse opportunities
        underused_datasets = [name for name, count in analysis["dataset_usage"].items() if count == 1]
        for dataset in underused_datasets[:5]:  # Limit to top 5
            opportunities.append({
                "type": "dataset_reuse",
                "description": f"Apply different methodologies to {dataset}",
                "dataset": dataset,
                "rationale": "This dataset has been underutilized in research"
            })
        
        # Reproducibility improvement opportunities
        if analysis["reproducibility_scores"]:
            avg_score = sum(analysis["reproducibility_scores"]) / len(analysis["reproducibility_scores"])
            if avg_score < 0.7:
                opportunities.append({
                    "type": "reproducibility_improvement",
                    "description": "Develop better reproducibility practices",
                    "current_avg_score": avg_score,
                    "rationale": "Current research shows low reproducibility scores"
                })
        
        return opportunities
    
    def _count_combined_tool_usage(self, tool1: str, tool2: str) -> int:
        """Count how many papers use both tools."""
        papers_with_tool1 = set()
        papers_with_tool2 = set()
        
        # Find papers using each tool
        for subj, pred, obj in self.graph:
            if pred == SCIENTIFIC.usesTool:
                tool_name = self._get_entity_name(obj)
                if tool_name == tool1:
                    papers_with_tool1.add(subj)
                elif tool_name == tool2:
                    papers_with_tool2.add(subj)
        
        return len(papers_with_tool1.intersection(papers_with_tool2))
    
    def generate_hypotheses_with_llm(self, analysis: Dict[str, Any], 
                                   opportunities: List[Dict[str, Any]], 
                                   num_hypotheses: int = 5,
                                   focus_area: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate hypotheses using LLM based on graph analysis."""
        if not self.api_key:
            return self._generate_rule_based_hypotheses(analysis, opportunities, num_hypotheses)
        
        # Prepare context for LLM
        context = self._prepare_llm_context(analysis, opportunities, focus_area)
        
        try:
            if "gpt" in self.model.lower():
                return self._generate_with_openai(context, num_hypotheses)
            elif "claude" in self.model.lower():
                return self._generate_with_anthropic(context, num_hypotheses)
            elif "gemini" in self.model.lower():
                return self._generate_with_gemini(context, num_hypotheses)
            else:
                logger.warning(f"Unknown model {self.model}, falling back to rule-based generation")
                return self._generate_rule_based_hypotheses(analysis, opportunities, num_hypotheses)
        except Exception as e:
            logger.error(f"LLM hypothesis generation failed: {e}")
            return self._generate_rule_based_hypotheses(analysis, opportunities, num_hypotheses)
    
    def _prepare_llm_context(self, analysis: Dict[str, Any], 
                           opportunities: List[Dict[str, Any]], 
                           focus_area: Optional[str]) -> str:
        """Prepare context for LLM hypothesis generation."""
        context = f"""
Based on the following analysis of a scientific knowledge graph, generate novel research hypotheses:

GRAPH STATISTICS:
- Papers: {analysis['entity_counts'].get('https://schema.org/ScholarlyArticle', 0)}
- Authors: {analysis['entity_counts'].get('https://schema.org/Person', 0)}
- Tools: {analysis['entity_counts'].get('https://scientific.org/SoftwareTool', 0)}
- Datasets: {analysis['entity_counts'].get('https://schema.org/Dataset', 0)}

POPULAR TOOLS:
{', '.join(list(analysis['tool_usage'].keys())[:10])}

POPULAR DATASETS:
{', '.join(list(analysis['dataset_usage'].keys())[:10])}

REPRODUCIBILITY INSIGHTS:
- Average reproducibility score: {sum(analysis['reproducibility_scores'])/len(analysis['reproducibility_scores']) if analysis['reproducibility_scores'] else 'N/A'}
- Number of assessed repositories: {len(analysis['reproducibility_scores'])}

RESEARCH OPPORTUNITIES:
"""
        
        for opp in opportunities[:5]:  # Limit to top 5 opportunities
            context += f"- {opp['description']}: {opp['rationale']}\n"
        
        if focus_area:
            context += f"\nFOCUS AREA: {focus_area}\n"
        
        context += """
Generate research hypotheses that:
1. Combine existing tools/datasets in novel ways
2. Address reproducibility challenges
3. Explore underutilized resources
4. Propose methodological improvements
5. Suggest cross-disciplinary applications

Return the response as a JSON array with this structure:
[
  {
    "hypothesis": "Clear, testable research hypothesis",
    "rationale": "Why this hypothesis is worth investigating",
    "methodology": "Suggested approach to test the hypothesis",
    "required_resources": ["tool1", "dataset1", "etc"],
    "expected_impact": "Potential scientific impact",
    "feasibility": "high/medium/low",
    "novelty_score": 0.8
  }
]
"""
        return context
    
    def _generate_with_openai(self, context: str, num_hypotheses: int) -> List[Dict[str, Any]]:
        """Generate hypotheses using OpenAI API."""
        import openai
        
        client = openai.OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a scientific research expert who generates novel, testable hypotheses based on knowledge graph analysis. Return only valid JSON."},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        hypotheses = json.loads(result)
        return hypotheses[:num_hypotheses]
    
    def _generate_with_anthropic(self, context: str, num_hypotheses: int) -> List[Dict[str, Any]]:
        """Generate hypotheses using Anthropic Claude API."""
        import anthropic
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        
        result = response.content[0].text
        hypotheses = json.loads(result)
        return hypotheses[:num_hypotheses]

    def _generate_with_gemini(self, context: str, num_hypotheses: int) -> List[Dict[str, Any]]:
        """Generate hypotheses using Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(
            context,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
            )
        )

        result = response.text
        hypotheses = json.loads(result)
        return hypotheses[:num_hypotheses]

    def _generate_rule_based_hypotheses(self, analysis: Dict[str, Any],
                                      opportunities: List[Dict[str, Any]], 
                                      num_hypotheses: int) -> List[Dict[str, Any]]:
        """Generate hypotheses using rule-based approach when no LLM is available."""
        hypotheses = []
        
        # Generate hypotheses from opportunities
        for i, opp in enumerate(opportunities[:num_hypotheses]):
            if opp["type"] == "tool_combination":
                hypothesis = {
                    "hypothesis": f"Combining {opp['tools'][0]} and {opp['tools'][1]} will improve research outcomes",
                    "rationale": opp["rationale"],
                    "methodology": f"Develop integrated workflow using both {opp['tools'][0]} and {opp['tools'][1]}",
                    "required_resources": opp["tools"],
                    "expected_impact": "Improved computational efficiency and accuracy",
                    "feasibility": "medium",
                    "novelty_score": 0.7
                }
            elif opp["type"] == "dataset_reuse":
                hypothesis = {
                    "hypothesis": f"Applying machine learning methods to {opp['dataset']} will reveal new insights",
                    "rationale": opp["rationale"],
                    "methodology": f"Apply modern ML techniques to analyze {opp['dataset']}",
                    "required_resources": [opp["dataset"], "machine learning tools"],
                    "expected_impact": "Discovery of previously unknown patterns",
                    "feasibility": "high",
                    "novelty_score": 0.6
                }
            else:
                hypothesis = {
                    "hypothesis": "Improving research reproducibility through automated validation",
                    "rationale": "Current reproducibility scores are low",
                    "methodology": "Develop automated reproducibility assessment tools",
                    "required_resources": ["containerization", "automated testing"],
                    "expected_impact": "Higher reproducibility across scientific research",
                    "feasibility": "medium",
                    "novelty_score": 0.5
                }
            
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def generate_research_report(self, graph_file: str, num_hypotheses: int = 5, 
                               focus_area: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive research report with hypotheses."""
        # Load and analyze graph
        self.load_knowledge_graph(graph_file)
        analysis = self.analyze_graph_patterns()
        opportunities = self.find_research_opportunities(analysis)
        
        # Generate hypotheses
        hypotheses = self.generate_hypotheses_with_llm(
            analysis, opportunities, num_hypotheses, focus_area
        )
        
        # Create comprehensive report
        report = {
            "generation_timestamp": datetime.now().isoformat(),
            "source_graph": graph_file,
            "focus_area": focus_area,
            "graph_analysis": {
                "total_triples": len(self.graph),
                "entity_counts": dict(analysis["entity_counts"]),
                "popular_tools": dict(list(analysis["tool_usage"].most_common(10))),
                "popular_datasets": dict(list(analysis["dataset_usage"].most_common(10))),
                "avg_reproducibility_score": sum(analysis["reproducibility_scores"])/len(analysis["reproducibility_scores"]) if analysis["reproducibility_scores"] else None
            },
            "research_opportunities": opportunities,
            "generated_hypotheses": hypotheses,
            "summary": {
                "total_hypotheses": len(hypotheses),
                "avg_novelty_score": sum(h.get("novelty_score", 0) for h in hypotheses) / len(hypotheses) if hypotheses else 0,
                "feasibility_distribution": self._analyze_feasibility(hypotheses)
            }
        }
        
        return report
    
    def _analyze_feasibility(self, hypotheses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze feasibility distribution of hypotheses."""
        distribution = {"high": 0, "medium": 0, "low": 0}
        for h in hypotheses:
            feasibility = h.get("feasibility", "medium")
            if feasibility in distribution:
                distribution[feasibility] += 1
        return distribution


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Generate research hypotheses from knowledge graph")
    parser.add_argument("--graph", "-g", required=True, help="Path to RDF knowledge graph file")
    parser.add_argument("--output", "-o", default="hypotheses.json", help="Output hypotheses file")
    parser.add_argument("--num-hypotheses", "-n", type=int, default=5, help="Number of hypotheses to generate")
    parser.add_argument("--focus-area", "-f", help="Optional focus area for hypothesis generation")
    parser.add_argument("--model", "-m", default="gpt-4", help="LLM model to use")
    parser.add_argument("--api-key", help="API key (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    try:
        generator = HypothesisGenerator(api_key=args.api_key, model=args.model)
        report = generator.generate_research_report(
            args.graph, args.num_hypotheses, args.focus_area
        )
        
        # Save report
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info(f"Generated {len(report['generated_hypotheses'])} hypotheses")
        print(f"✅ Hypothesis generation complete: {args.output}")
        print(f"🧬 Generated {len(report['generated_hypotheses'])} hypotheses")
        print(f"📊 Average novelty score: {report['summary']['avg_novelty_score']:.2f}")
        
        # Print first hypothesis as example
        if report['generated_hypotheses']:
            first_hyp = report['generated_hypotheses'][0]
            print(f"\n💡 Example hypothesis:")
            print(f"   {first_hyp['hypothesis']}")
            print(f"   Feasibility: {first_hyp.get('feasibility', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Hypothesis generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
