"""Examples of using the AI Router"""

from router import AIRouter
import os
from datetime import datetime


# Global file handle for saving output
output_file = None


def setup_output_file():
    """Setup the output file for saving prints"""
    global output_file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"router_examples_output_{timestamp}.txt"
    output_file = open(filename, 'w', encoding='utf-8')
    return filename


def cleanup_output_file():
    """Close the output file"""
    global output_file
    if output_file:
        output_file.close()


def print_and_save(*args, **kwargs):
    """Print to console and save to file"""
    global output_file
    # Print to console
    print(*args, **kwargs)
    # Save to file
    if output_file:
        print(*args, **kwargs, file=output_file)
        output_file.flush()  # Ensure immediate write


def print_header(title, width=80):
    """Print a fancy header"""
    print_and_save("\n" + "═" * width)
    print_and_save(f"║ {title.center(width - 4)} ║")
    print_and_save("═" * width)


def print_section(title):
    """Print a section divider"""
    print_and_save(f"\n{'─' * 20} {title} {'─' * 20}")


def print_result_box(prompt, result, response_preview=None):
    """Print results in a nice box format"""
    box_width = 70
    print_and_save("\n┌" + "─" * box_width + "┐")
    
    # Prompt
    print_and_save("│ " + "🤔 PROMPT:".ljust(box_width - 2) + " │")
    wrapped_prompt = prompt[:box_width - 4]
    if len(prompt) > box_width - 4:
        wrapped_prompt += "..."
    print_and_save("│ " + wrapped_prompt.ljust(box_width - 2) + " │")
    
    print_and_save("├" + "─" * box_width + "┤")
    
    # Model selection
    print_and_save("│ " + f"🤖 MODEL: {result['selected_model']}".ljust(box_width - 2) + " │")
    print_and_save("│ " + f"📊 CONFIDENCE: {result['confidence']:.2%}".ljust(box_width - 2) + " │")
    
    # Reasoning
    print_and_save("├" + "─" * box_width + "┤")
    print_and_save("│ " + "💭 REASONING:".ljust(box_width - 2) + " │")
    reasoning_lines = []
    words = result['reasoning'].split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > box_width - 4:
            reasoning_lines.append(current_line)
            current_line = word
        else:
            current_line = current_line + " " + word if current_line else word
    if current_line:
        reasoning_lines.append(current_line)
    
    for line in reasoning_lines[:3]:  # Show max 3 lines
        print_and_save("│ " + line.ljust(box_width - 2) + " │")
    
    # Response preview if provided
    if response_preview:
        print_and_save("├" + "─" * box_width + "┤")
        print_and_save("│ " + "💬 RESPONSE:".ljust(box_width - 2) + " │")
        preview = response_preview[:box_width - 4]
        if len(response_preview) > box_width - 4:
            preview += "..."
        print_and_save("│ " + preview.ljust(box_width - 2) + " │")
    
    print_and_save("└" + "─" * box_width + "┘")


def print_parallel_results(mode, metadata, response_preview):
    """Print results for parallel modes in a fancy format"""
    box_width = 75
    print_and_save("\n╔" + "═" * box_width + "╗")
    print_and_save("║ " + f"🚀 {mode.upper()} RESULTS".center(box_width - 2) + " ║")
    print_and_save("╠" + "═" * box_width + "╣")
    
    if mode == "parallelbest":
        print_and_save("║ " + f"🏆 BEST MODEL: {metadata['selected_model']}".ljust(box_width - 2) + " ║")
        print_and_save("║ " + f"📝 REASONING: {metadata['evaluation']['reasoning'][:50]}...".ljust(box_width - 2) + " ║")
        print_and_save("╠" + "═" * box_width + "╣")
        print_and_save("║ " + "📊 MODEL RANKING:".ljust(box_width - 2) + " ║")
        for i, model in enumerate(metadata['evaluation']['ranking'][:3], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print_and_save("║ " + f"  {medal} {i}. {model}".ljust(box_width - 2) + " ║")
    else:  # parallelsynthetize
        print_and_save("║ " + f"🔧 MODELS USED: {', '.join(metadata['models_used'])}".ljust(box_width - 2) + " ║")
    
    print_and_save("╠" + "═" * box_width + "╣")
    print_and_save("║ " + "💬 SYNTHESIZED RESPONSE:".ljust(box_width - 2) + " ║")
    preview = response_preview[:box_width - 4]
    if len(response_preview) > box_width - 4:
        preview += "..."
    print_and_save("║ " + preview.ljust(box_width - 2) + " ║")
    
    print_and_save("╠" + "═" * box_width + "╣")
    print_and_save("║ " + "📋 INDIVIDUAL MODEL RESPONSES:".ljust(box_width - 2) + " ║")
    for resp in metadata['all_responses'][:3]:
        model_line = f"  • {resp['model_name']}: {resp['response'][:40]}..."
        print_and_save("║ " + model_line.ljust(box_width - 2) + " ║")
    
    print_and_save("╚" + "═" * box_width + "╝")


def example_basic_routing():
    """Example of basic routing"""
    print_header("🎯 BASIC ROUTING EXAMPLE", 80)
    
    router = AIRouter()
    
    # Test various prompts
    test_prompts = [
        "Write a Python function to calculate fibonacci in fibonacci.py",
        "How are you? Use Gemini model",
        "List all cities in Europe.",
        "Prove that sqrt(2) is irrational",
        "Write a Python function to calculate fibonacci in fibonacci.py in the current repo"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print_and_save(f"\n{'='*30} Test {i}/{len(test_prompts)} {'='*30}")
        
        # First analyze which model would be best
        result = router.analyze_prompt(prompt)
        
        # Actually call the selected model
        messages = [{"role": "user", "content": prompt}]
        try:
            response = router.route(messages)  # Limit tokens for demo
            actual_response = response.choices[0].message.content
            print_result_box(prompt, result, actual_response)
        except Exception as e:
            print_result_box(prompt, result)
            print_and_save(f"❌ Error calling {result['selected_model']}: {str(e)}")


def example_parallelbest_mode():
    """Example of parallelbest mode - calls all models and picks the best response"""
    print_header("🏆 PARALLELBEST MODE EXAMPLE", 80)
    
    router = AIRouter()
    
    messages = [{"role": "user", "content": "Make factorial.py with a factorial function"}]
    
    try:
        response, metadata = router.parallelbest_route(messages)
        response_preview = response.choices[0].message.content
        print_parallel_results("parallelbest", metadata, response_preview)
    except Exception as e:
        print_and_save(f"\n❌ Error in parallelbest mode: {str(e)}")


def example_parallelsynthetize_mode():
    """Example of parallelsynthetize mode - synthesizes responses from all models"""
    print_header("🔀 PARALLELSYNTHETIZE MODE EXAMPLE", 80)
    
    router = AIRouter()
    
    messages = [{"role": "user", "content": "Make subtraction.py with a subtraction function"}]
    
    try:
        response, metadata = router.parallelsynthetize_route(messages)
        response_preview = response.choices[0].message.content
        print_parallel_results("parallelsynthetize", metadata, response_preview)
    except Exception as e:
        print_and_save(f"\n❌ Error in parallelsynthetize mode: {str(e)}")


def example_route_with_metadata():
    """Example showing how to get routing metadata"""
    print_header("📊 ROUTE WITH METADATA EXAMPLE", 80)
    
    router = AIRouter()
    
    messages = [{"role": "user", "content": "Explain quantum computing"}]
    
    # Get both response and metadata
    response, metadata = router.route_with_metadata(messages)
    
    # Create fancy output
    print_and_save("\n╭─────────────────────────────────────────────────────────────────╮")
    print_and_save("│                      📈 ROUTING METADATA                        │")
    print_and_save("├─────────────────────────────────────────────────────────────────┤")
    print_and_save(f"│ 🤖 Selected Model: {metadata['selected_model']:<43} │")
    print_and_save(f"│ 🆔 Model ID: {metadata['model_id']:<49} │")
    print_and_save(f"│ 📊 Confidence: {metadata['confidence']:<47.2%} │")
    print_and_save("├─────────────────────────────────────────────────────────────────┤")
    print_and_save("│ 💭 Reasoning:                                                   │")
    
    # Wrap reasoning text
    reasoning = metadata['reasoning']
    words = reasoning.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > 60:
            lines.append(current_line)
            current_line = word
        else:
            current_line = current_line + " " + word if current_line else word
    if current_line:
        lines.append(current_line)
    
    for line in lines[:3]:
        print_and_save(f"│   {line:<61} │")
    
    print_and_save("├─────────────────────────────────────────────────────────────────┤")
    print_and_save("│ 💬 Response Preview:                                            │")
    response_text = response.choices[0].message.content[:120]
    response_lines = []
    words = response_text.split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > 60:
            response_lines.append(current_line)
            current_line = word
        else:
            current_line = current_line + " " + word if current_line else word
    if current_line:
        response_lines.append(current_line)
    
    for line in response_lines[:2]:
        print_and_save(f"│   {line:<61} │")
    
    print_and_save("╰─────────────────────────────────────────────────────────────────╯")


def run_all_examples():
    # Setup output file
    filename = setup_output_file()
    print_and_save(f"📝 Output will be saved to: {filename}")
    
    print_and_save("\n" + "🌟" * 40)
    print_and_save("🚀 AI ROUTER EXAMPLES SHOWCASE 🚀".center(80))
    print_and_save("🌟" * 40)
    
    example_basic_routing()
    print_and_save("\n" + "~" * 80 + "\n")
    
    example_parallelbest_mode()
    print_and_save("\n" + "~" * 80 + "\n")
    
    example_parallelsynthetize_mode()
    print_and_save("\n" + "~" * 80 + "\n")
    
    example_route_with_metadata()
    
    print_and_save("\n" + "🌟" * 40)
    print_and_save("✅ ALL EXAMPLES COMPLETED! ✅".center(80))
    print_and_save("🌟" * 40 + "\n")
    
    # Cleanup
    cleanup_output_file()
    print(f"📁 Output saved to: {filename}")


if __name__ == "__main__":
    run_all_examples()