# Pipeline 2.0: Frågedriven Smart Block Factory
"""
Frågedriven Smart Block-generering som använder SECONDARY-avrop
för att identifiera kunskapsluckor och fylla dem med PRIMARY-baserade block.

Komponenter:
- extractor.py: Extraherar frågor från SECONDARY-avrop
- tester.py: Testar frågor mot P-Bot + Judge-LLM
- creator.py: Skapar nya Smart Blocks vid GAP
- refiner.py: Förbättrar befintliga blocks vid IMPROVE
- run_pipeline.py: Orchestrator med throttling
"""







