import sys
from pathlib import Path

# Add the visualization module to path (sibling directory)
sys.path.insert(0, str(Path(__file__).parent.parent / "pocketflow-visualization"))
from flow import create_chain_of_thought_flow
from visualize import visualize_flow


def _try_init_canvas(question: str) -> dict:
    """Attempt to connect to a running llm-canvas server and create a canvas.
    Returns a dict of canvas keys to inject into shared, or empty dict on failure.
    """
    try:
        from llm_canvas.canvas_client import CanvasClient

        client = CanvasClient()
        canvas = client.create_canvas(
            title=f"ChainOfThought: {question[:60]}",
            description=question,
        )
        print("llm-canvas canvas created")
        print("  → View at http://localhost:8000")
        return {
            "_canvas": canvas,
            "_canvas_parent_id": None,
        }
    except Exception as e:
        print(f"llm-canvas not available (run 'llm-canvas server' first): {e}")
        return {}


def main():
    # Default question
    default_question = "I want to build an LLM agent using pocketflow, I want this agent to perform multi-step reasoning to assign tasks to a certain timeslot, basing that assignment on the context of a users calendar and preferences."
    # Get question from command line if provided with --
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break

    print(f"🤔 Processing question: {question}")

    # Create the flow
    cot_flow = create_chain_of_thought_flow()

    # Visualize the flow graph and open it in the browser before running
    viz_output_dir = str(Path(__file__).parent / "viz")
    visualize_flow(
        flow=cot_flow,
        flow_name="Chain of Thought",
        output_dir=viz_output_dir,
    )

    # Set up shared state
    shared = {
        "problem": question,
        "thoughts": [],
        "current_thought_number": 0,
        "total_thoughts_estimate": 4,
        "solution": None,
    }

    # Optionally connect to llm-canvas for conversation visualization
    shared.update(_try_init_canvas(question))

    # Run the flow
    cot_flow.run(shared)

    # Keep the visualization server alive after the flow completes
    try:
        input("\nVisualization still available in browser. Press Enter to exit...")
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == "__main__":
    main()
