"""
Pentagon Protocol - Experiment Runner
Run experiments with enhanced error handling
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from src.crew import PentagonCrew, BaselineCrew


def load_prompts(filepath: str = "data/prompts/vibe_prompts.json") -> list:
    """Load vibe prompts from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
        prompts = data.get("prompts", [])

    return prompts


def run_single_test(prompt: str = "Build a simple calculator"):
    """Run a single quick test."""
    print("\n" + "="*60)
    print("PENTAGON PROTOCOL - SINGLE TEST")
    print("="*60)
    
    crew = PentagonCrew(verbose=True)
    result = crew.run(prompt)
    
    print("\n" + "="*60)
    print("RESULT SUMMARY")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Phases Succeeded: {result.get('phases_succeeded', 0)}/5")
    print(f"Execution Time: {result.get('execution_time_seconds', 0)}s")
    print(f"Output Directory: {result.get('project_dir', 'N/A')}")
    
    if result.get('errors'):
        print(f"Errors: {result['errors']}")
    
    return result


def run_comparison(prompt: str):
    """Run both Pentagon and Baseline for comparison."""
    print("\n" + "="*60)
    print("COMPARISON: PENTAGON vs BASELINE")
    print(f"Prompt: {prompt}")
    print("="*60)
    
    # Pentagon
    print("\n--- Running Pentagon Protocol ---")
    pentagon = PentagonCrew(verbose=True)
    pentagon_result = pentagon.run(prompt)
    
    # Baseline
    print("\n--- Running Baseline (Single Agent) ---")
    baseline = BaselineCrew(verbose=True)
    baseline_result = baseline.run(prompt)
    
    # Summary
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    print(f"Pentagon: Success={pentagon_result['success']}, Time={pentagon_result.get('execution_time_seconds', 0)}s")
    print(f"Baseline: Success={baseline_result['success']}, Time={baseline_result.get('execution_time_seconds', 0)}s")
    
    return {
        "prompt": prompt,
        "pentagon": pentagon_result,
        "baseline": baseline_result
    }


def run_full_experiment():
    """Run full experiment with all prompts."""
    prompts = load_prompts()
    
    print("\n" + "="*60)
    print("FULL EXPERIMENT - ALL PROMPTS")
    print(f"Total Prompts: {len(prompts)}")
    print("="*60)
    
    results = []
    for i, prompt_data in enumerate(prompts):
        prompt_id = prompt_data.get("id", f"VP{i+1:02d}")
        prompt_text = prompt_data.get("prompt", "")
        complexity = prompt_data.get("complexity", "unknown")
        expected_features = prompt_data.get("expected_features", [])
            
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(prompts)}] {prompt_id} ({complexity})")
        print(f"Prompt: {prompt_text[:60]}...")
        print("="*60)

        comparison = run_comparison(f"{prompt_text}, which sould have minimum features : {', '.join(expected_features)}")
        comparison["prompt_id"] = prompt_id
        comparison["complexity"] = complexity
        comparison["expected_features"] = expected_features
        results.append(comparison)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = Path("output") / f"full_experiment_{timestamp}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            "experiment_date": datetime.now().isoformat(),
            "total_prompts": len(prompts),
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {results_file}")
    
    # Summary
    pentagon_success = sum(1 for r in results if r["pentagon"]["success"])
    baseline_success = sum(1 for r in results if r["baseline"]["success"])
    
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Pentagon Success Rate: {pentagon_success}/{len(prompts)} ({100*pentagon_success/len(prompts):.1f}%)")
    print(f"Baseline Success Rate: {baseline_success}/{len(prompts)} ({100*baseline_success/len(prompts):.1f}%)")
    
    return results


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--full":
            run_full_experiment()
        elif arg == "--help":
            print("Usage:")
            print("  python run_experiment.py              # Interactive menu")
            print("  python run_experiment.py --full       # Run all prompts")
            print("  python run_experiment.py 'prompt'     # Run single prompt")
        else:
            run_single_test(arg)
    else:
        # Interactive menu
        print("\nPentagon Protocol - Experiment Runner")
        print("1. Quick test (calculator)")
        print("2. Custom prompt")
        print("3. Full experiment (all prompts)")
        print("4. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            run_single_test()
        elif choice == "2":
            prompt = input("Enter vibe prompt: ").strip()
            if prompt:
                run_single_test(prompt)
        elif choice == "3":
            run_full_experiment()
        else:
            print("Exiting.")


if __name__ == "__main__":
    main()
