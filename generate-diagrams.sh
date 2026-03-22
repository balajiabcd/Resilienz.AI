#!/bin/bash
# generate-diagrams.sh
# Regenerates all Mermaid diagrams from source files

echo "Generating architecture diagram..."
npx mmdc -i mermaid/architecture.mmd -o images/architecture.png -b transparent -w 2400 -H 1600 -s 2

echo "Generating agent flow diagram..."
npx mmdc -i mermaid/agent-flow.mmd -o images/agent-flow.png -b transparent -w 2000 -H 1800 -s 2

echo "Generating simulation diagram..."
npx mmdc -i mermaid/simulation.mmd -o images/simulation.png -b transparent -w 1600 -H 1200 -s 2

echo "Done! Check the images/ directory."
