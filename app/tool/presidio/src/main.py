import argparse
import sys
import os
import pandas as pd
from datetime import datetime
from .generator import generate_dummy_data
from .processor import process_dataframe_to_csv
from .simulator import run_simulation

def main():
    parser = argparse.ArgumentParser(description="Calendar Data Anonymizer & RAG Simulator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: generate (Dataset generation)
    parser_gen = subparsers.add_parser("generate", help="Generate anonymized training data")
    parser_gen.add_argument("--input", help="Input CSV file path. If omitted, generates dummy data.")
    parser_gen.add_argument("--output", help="Output CSV file path")
    parser_gen.add_argument("--dummy-count", type=int, default=500, help="Number of dummy records (default: 500)")

    # Command: simulate (RAG simulation)
    parser_sim = subparsers.add_parser("simulate", help="Run RAG simulation")
    parser_sim.add_argument("--date", required=True, help="Target date (YYYY/MM/DD HH:MM)")
    parser_sim.add_argument("--model-data", default="training_data.csv", help="Path to training CSV for prediction model")

    args = parser.parse_args()

    if args.command == "generate":
        output_file = args.output
        if args.input:
            if not output_file:
                output_file = "anonymized_dataset.csv"
            print(f"Reading from {args.input}...")
            try:
                df = pd.read_csv(args.input)
                process_dataframe_to_csv(df, output_file)
            except Exception as e:
                print(f"Error reading CSV: {e}")
                sys.exit(1)
        else:
            # Dummy mode
            if not output_file:
                os.makedirs("generated", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"generated/{timestamp}_generated.csv"
            
            print("No input file provided. Generating dummy data...")
            df = generate_dummy_data(args.dummy_count)
            process_dataframe_to_csv(df, output_file)

    elif args.command == "simulate":
        if not os.path.exists(args.model_data):
            print(f"Error: Training data '{args.model_data}' not found.")
            print("Run 'uv run python -m src.main generate --output training_data.csv' first.")
            sys.exit(1)
        
        run_simulation(args.date, args.model_data)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
