#!/usr/bin/env python3
"""
Evaluation framework for parallelsynthetize_route function
This evaluates the function's ability to synthesize responses from multiple AI models
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from router import AIRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ParallelSynthetizeEvaluator:
    """Evaluator for the parallelsynthetize_route function"""
    
    def __init__(self):
        # Initialize router with configuration
        self.config = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            },
            "claude_code": {
                "api_key": "dummy"  # Claude Code runs locally
            },
            "xai": {
                "api_key": os.getenv("XAI_API_KEY", ""),
                "base_url": "https://api.x.ai/v1"
            },
            "google": {
                "api_key": os.getenv("GOOGLE_API_KEY", "")
            }
        }
        
        self.router = AIRouter(self.config)
        
        # Evaluation metrics
        self.metrics = {
            "total_tests": 0,
            "successful_syntheses": 0,
            "failed_syntheses": 0,
            "average_response_time": 0,
            "model_participation": {},
            "synthesis_quality_scores": [],
            "category_performance": {}
        }
    
    def create_test_suite(self) -> List[Dict[str, Any]]:
        """Create a comprehensive test suite for different types of tasks"""
        return [
            # Coding tasks
            {
                "id": "code_001",
                "category": "coding",
                "prompt": "Write a Python function that implements binary search on a sorted array. Include error handling and documentation.",
                "expected_features": ["function definition", "error handling", "documentation", "time complexity"]
            },
            {
                "id": "code_002",
                "category": "coding",
                "prompt": "Create a JavaScript class for a linked list with methods for insertion, deletion, and searching.",
                "expected_features": ["class definition", "insertion method", "deletion method", "search method"]
            },
            
            # Reasoning tasks
            {
                "id": "reason_001",
                "category": "reasoning",
                "prompt": "Solve this logic puzzle: Three friends (Alice, Bob, and Charlie) each have a different pet (cat, dog, bird). Alice doesn't have the cat. Bob doesn't have the dog. Charlie doesn't have the bird. What pet does each person have?",
                "expected_features": ["logical deduction", "step-by-step reasoning", "final answer"]
            },
            {
                "id": "reason_002",
                "category": "reasoning",
                "prompt": "Explain the prisoner's dilemma and why cooperation is difficult to achieve in this scenario.",
                "expected_features": ["game theory explanation", "payoff matrix", "Nash equilibrium", "real-world applications"]
            },
            
            # Creative tasks
            {
                "id": "creative_001",
                "category": "creative",
                "prompt": "Write a short story (200 words) about a time traveler who accidentally changes history by stepping on a butterfly.",
                "expected_features": ["narrative structure", "time travel element", "butterfly effect", "consequences"]
            },
            
            # Analysis tasks
            {
                "id": "analysis_001",
                "category": "analysis",
                "prompt": "Analyze the pros and cons of remote work for both employees and employers, considering productivity, work-life balance, and company culture.",
                "expected_features": ["employee benefits", "employee drawbacks", "employer benefits", "employer drawbacks"]
            },
            
            # General knowledge
            {
                "id": "general_001",
                "category": "general",
                "prompt": "Explain photosynthesis in simple terms that a 10-year-old could understand.",
                "expected_features": ["simple language", "basic process explanation", "importance to life", "analogy or comparison"]
            }
        ]
    
    def evaluate_synthesis_quality(self, 
                                 prompt: str, 
                                 synthesized_response: str, 
                                 individual_responses: List[Dict[str, Any]],
                                 expected_features: List[str]) -> Dict[str, Any]:
        """Evaluate the quality of a synthesized response"""
        
        # Check if synthesis includes expected features
        features_found = []
        for feature in expected_features:
            if feature.lower() in synthesized_response.lower():
                features_found.append(feature)
        
        feature_coverage = len(features_found) / len(expected_features) if expected_features else 0
        
        # Calculate synthesis metrics
        synthesis_length = len(synthesized_response)
        avg_individual_length = sum(len(r['response']) for r in individual_responses) / len(individual_responses) if individual_responses else 0
        
        # Check if synthesis combines insights from multiple models
        unique_insights = 0
        for response in individual_responses:
            # Simple heuristic: check if any substantial part of individual response is in synthesis
            response_text = response['response'][:100]  # Check first 100 chars
            if response_text in synthesized_response:
                unique_insights += 1
        
        insight_coverage = unique_insights / len(individual_responses) if individual_responses else 0
        
        # Calculate overall quality score (0-10)
        quality_score = (
            feature_coverage * 4 +  # 40% weight on expected features
            insight_coverage * 3 +  # 30% weight on combining insights
            min(synthesis_length / avg_individual_length, 1) * 3  # 30% weight on comprehensiveness
        )
        
        return {
            "quality_score": round(quality_score, 2),
            "feature_coverage": feature_coverage,
            "features_found": features_found,
            "insight_coverage": insight_coverage,
            "synthesis_length": synthesis_length,
            "avg_individual_length": avg_individual_length
        }
    
    def run_evaluation(self):
        """Run the full evaluation suite"""
        test_suite = self.create_test_suite()
        evaluation_results = []
        
        print("Starting evaluation of parallelsynthetize_route...")
        print(f"Running {len(test_suite)} test cases")
        print("=" * 80)
        
        for test_case in test_suite:
            print(f"\nTest {test_case['id']}: {test_case['category']}")
            print(f"Prompt: {test_case['prompt'][:80]}...")
            
            start_time = time.time()
            
            try:
                # Prepare messages
                messages = [{"role": "user", "content": test_case['prompt']}]
                
                # Call parallelsynthetize_route
                response, metadata = self.router.parallelsynthetize_route(messages, max_tokens=1000)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Extract synthesized response
                synthesized_content = response.choices[0].message.content
                
                # Evaluate synthesis quality
                quality_eval = self.evaluate_synthesis_quality(
                    test_case['prompt'],
                    synthesized_content,
                    metadata.get('all_responses', []),
                    test_case.get('expected_features', [])
                )
                
                # Record results
                result = {
                    "test_id": test_case['id'],
                    "category": test_case['category'],
                    "prompt": test_case['prompt'],
                    "success": True,
                    "response_time": response_time,
                    "synthesized_response": synthesized_content,
                    "models_used": metadata.get('models_used', []),
                    "best_individual_model": metadata.get('best_individual_model', 'Unknown'),
                    "quality_evaluation": quality_eval,
                    "task_info": metadata.get('task_info', {}),
                    "individual_scores": metadata.get('scoring', {}).get('scores', {})
                }
                
                evaluation_results.append(result)
                
                # Update metrics
                self.metrics["successful_syntheses"] += 1
                self.metrics["synthesis_quality_scores"].append(quality_eval['quality_score'])
                
                # Update category performance
                category = test_case['category']
                if category not in self.metrics["category_performance"]:
                    self.metrics["category_performance"][category] = {
                        "count": 0,
                        "avg_quality": 0,
                        "avg_response_time": 0
                    }
                
                cat_perf = self.metrics["category_performance"][category]
                cat_perf["count"] += 1
                cat_perf["avg_quality"] = (
                    (cat_perf["avg_quality"] * (cat_perf["count"] - 1) + quality_eval['quality_score']) 
                    / cat_perf["count"]
                )
                cat_perf["avg_response_time"] = (
                    (cat_perf["avg_response_time"] * (cat_perf["count"] - 1) + response_time) 
                    / cat_perf["count"]
                )
                
                # Update model participation
                for model in metadata.get('models_used', []):
                    if model not in self.metrics["model_participation"]:
                        self.metrics["model_participation"][model] = 0
                    self.metrics["model_participation"][model] += 1
                
                print(f"✓ Success (Quality: {quality_eval['quality_score']}/10, Time: {response_time:.2f}s)")
                print(f"  Models used: {', '.join(metadata.get('models_used', []))}")
                print(f"  Best individual: {metadata.get('best_individual_model', 'Unknown')}")
                
            except Exception as e:
                result = {
                    "test_id": test_case['id'],
                    "category": test_case['category'],
                    "prompt": test_case['prompt'],
                    "success": False,
                    "error": str(e)
                }
                evaluation_results.append(result)
                self.metrics["failed_syntheses"] += 1
                print(f"✗ Failed: {str(e)}")
        
        # Calculate final metrics
        self.metrics["total_tests"] = len(test_suite)
        if self.metrics["synthesis_quality_scores"]:
            self.metrics["average_quality_score"] = sum(self.metrics["synthesis_quality_scores"]) / len(self.metrics["synthesis_quality_scores"])
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"parallelsynthetize_evaluation_{timestamp}.json"
        
        output = {
            "evaluation_timestamp": timestamp,
            "metrics": self.metrics,
            "detailed_results": evaluation_results
        }
        
        with open(results_file, "w") as f:
            json.dump(output, f, indent=2)
        
        # Generate report
        self.generate_report(output, results_file)
    
    def generate_report(self, results: Dict[str, Any], results_file: str):
        """Generate a human-readable evaluation report"""
        print("\n" + "=" * 80)
        print("EVALUATION REPORT: parallelsynthetize_route")
        print("=" * 80)
        
        metrics = results["metrics"]
        
        print(f"\nOverall Performance:")
        print(f"  Total Tests: {metrics['total_tests']}")
        print(f"  Successful: {metrics['successful_syntheses']}")
        print(f"  Failed: {metrics['failed_syntheses']}")
        print(f"  Success Rate: {(metrics['successful_syntheses'] / metrics['total_tests'] * 100):.1f}%")
        
        if "average_quality_score" in metrics:
            print(f"  Average Quality Score: {metrics['average_quality_score']:.2f}/10")
        
        print(f"\nModel Participation:")
        for model, count in sorted(metrics["model_participation"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {count} tests")
        
        print(f"\nCategory Performance:")
        for category, perf in metrics["category_performance"].items():
            print(f"  {category}:")
            print(f"    - Tests: {perf['count']}")
            print(f"    - Avg Quality: {perf['avg_quality']:.2f}/10")
            print(f"    - Avg Response Time: {perf['avg_response_time']:.2f}s")
        
        print(f"\nDetailed results saved to: {results_file}")
        
        # Generate recommendations
        print("\nRecommendations:")
        avg_quality = metrics.get("average_quality_score", 0)
        if avg_quality < 6:
            print("  - Quality scores are below optimal. Consider improving synthesis prompts.")
        elif avg_quality < 8:
            print("  - Quality scores are good but have room for improvement.")
        else:
            print("  - Excellent quality scores! The synthesis is working well.")
        
        # Check for model failures
        failed_models = []
        for result in results["detailed_results"]:
            if not result["success"]:
                failed_models.append(result.get("error", "Unknown error"))
        
        if failed_models:
            print(f"  - Some tests failed. Common errors: {', '.join(set(failed_models)[:3])}")

if __name__ == "__main__":
    evaluator = ParallelSynthetizeEvaluator()
    evaluator.run_evaluation()