"""
task5_agent.py — AI Trip Planner Agent (Supports Groq and Anthropic)
"""
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from utils import load_routes, group_by_case, compute_edges, aggregate_edges

load_dotenv()

class TransitAgent:
    def __init__(self, csv_path):
        self.rows = load_routes(csv_path)
        self.cases = group_by_case(self.rows)
        self.edges = aggregate_edges(compute_edges(self.cases))
        self.stops = sorted(list(set(r["stop_name"] for r in self.rows)))
        self.routes = sorted(list(set(r["route_id"] for r in self.rows)))
        
        # Check for API Keys
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if self.groq_key:
            from groq import Groq
            self.client = Groq(api_key=self.groq_key)
            self.provider = "groq"
        elif self.anthropic_key:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.anthropic_key)
            self.provider = "anthropic"
        else:
            self.client = None
            self.provider = None

    def get_context(self):
        context = "You are a CDA Bus Route Assistant. Use the following transit data to answer user queries.\n\n"
        context += "Available Routes: " + ", ".join(self.routes) + "\n"
        context += "Available Stops: " + ", ".join(self.stops) + "\n\n"
        context += "Route Details:\n"
        
        # Group stops by route for context
        route_map = {}
        for r in self.rows:
            rid = r["route_id"]
            if rid not in route_map: route_map[rid] = []
            if r["stop_name"] not in route_map[rid]:
                route_map[rid].append(r["stop_name"])
        
        for rid, stops in route_map.items():
            context += f"- {rid}: " + " -> ".join(stops) + "\n"
        
        context += "\nTransition Durations (Averages):\n"
        for e in self.edges:
            context += f"- {e['from_stop']} to {e['to_stop']} ({e['route_id']}): {e['label']}\n"
            
        return context

    def query(self, user_input):
        if not self.client:
            return "Error: No API key found. Please set GROQ_API_KEY or ANTHROPIC_API_KEY in your .env file."
            
        try:
            system_prompt = self.get_context() + "\nBe concise. Ground your answers ONLY in the data provided. Do not hallucinate stops or routes."
            
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                )
                return completion.choices[0].message.content
            
            elif self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=500,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_input}
                    ]
                )
                return message.content[0].text
                
        except Exception as e:
            return f"Agent Error ({self.provider}): {str(e)}"

if __name__ == "__main__":
    # Test
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "routes.csv"
    agent = TransitAgent(str(csv_path))
    print(f"Using Provider: {agent.provider}")
    print(agent.query("How do I get from Khanna Pul to FAST University?"))
