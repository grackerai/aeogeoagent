#!/usr/bin/env python
import sys
import warnings
import argparse
import logging
from typing import Optional

from multi_agent_crew.crew import WeatherCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('multi_agent_crew.log')
    ]
)
logger = logging.getLogger(__name__)


def run() -> Optional[str]:
    """
    Run the crew to get weather information for a location.
    
    Returns:
        The crew's output result
    """
    parser = argparse.ArgumentParser(
        description='Get weather information for any location using AI agents'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='London',
        help='Location to get weather for (default: London)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    inputs = {
        'location': args.location
    }

    try:
        logger.info(f"Starting weather crew for location: {inputs['location']}")
        result = WeatherCrew().crew().kickoff(inputs=inputs)
        logger.info("Weather crew completed successfully")
        
        print("\n\n=== WEATHER REPORT ===\n")
        print(result.raw)
        
        return result.raw
    except KeyboardInterrupt:
        logger.warning("Weather crew interrupted by user")
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running crew: {e}", exc_info=True)
        print(f"\n\n❌ Error: {str(e)}")
        raise Exception(f"An error occurred while running the crew: {e}")


def train() -> None:
    """
    Train the crew for a given number of iterations.
    """
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments for training")
        print("Usage: multi_agent_crew train <n_iterations> <filename>")
        sys.exit(1)
    
    inputs = {
        "location": "London"
    }
    
    try:
        logger.info(f"Starting training with {sys.argv[1]} iterations")
        WeatherCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
        logger.info("Training completed successfully")
    except ValueError as e:
        logger.error(f"Invalid iteration count: {e}")
        print("Error: n_iterations must be a valid integer")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        raise Exception(f"An error occurred while training the crew: {e}")


def replay() -> None:
    """
    Replay the crew execution from a specific task.
    """
    if len(sys.argv) < 2:
        logger.error("No task ID provided for replay")
        print("Usage: multi_agent_crew replay <task_id>")
        sys.exit(1)
    
    try:
        logger.info(f"Replaying task: {sys.argv[1]}")
        WeatherCrew().crew().replay(task_id=sys.argv[1])
        logger.info("Replay completed successfully")
    except Exception as e:
        logger.error(f"Error during replay: {e}", exc_info=True)
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test() -> None:
    """
    Test the crew execution and returns the results.
    """
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments for testing")
        print("Usage: multi_agent_crew test <n_iterations> <eval_llm>")
        sys.exit(1)
    
    inputs = {
        "location": "London"
    }

    try:
        logger.info(f"Starting test with {sys.argv[1]} iterations")
        WeatherCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )
        logger.info("Testing completed successfully")
    except ValueError as e:
        logger.error(f"Invalid iteration count: {e}")
        print("Error: n_iterations must be a valid integer")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger() -> Optional[str]:
    """
    Run the crew with trigger payload.
    
    Returns:
        The crew's output result
    """
    import json

    if len(sys.argv) < 2:
        logger.error("No trigger payload provided")
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
        logger.info(f"Running with trigger payload: {trigger_payload}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "location": trigger_payload.get("location", "London")
    }

    try:
        result = WeatherCrew().crew().kickoff(inputs=inputs)
        logger.info("Trigger-based execution completed successfully")
        return result.raw
    except Exception as e:
        logger.error(f"Error running crew with trigger: {e}", exc_info=True)
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
