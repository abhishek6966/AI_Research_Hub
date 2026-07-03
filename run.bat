@echo off
start "Data Extraction Pipeline" /wait .\.venv\Scripts\python.exe -u run_extraction.py %*
