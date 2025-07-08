#!/bin/bash
# Ejecuta pruebas unitarias y de integración
python -m pytest tests/ -v --cov=src --cov-report=term-missing