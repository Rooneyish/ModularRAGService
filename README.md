# ModularRAGService

A lightweight, high-performance **Agentic RAG (Retrieval-Augmented Generation) Service** built entirely with open-source infrastructure. 

Instead of relying on heavy, restrictive frameworks like LangChain or LlamaIndex, this project uses native SDKs to handle a custom RAG loop, multi-turn conversation memory, and model preloading. It also features a zero-dependency agent system that intercepts natural language interview booking requests via custom XML tags (`<BOOKING>`), extracts structured data parameters, and persists them into a relational database completely locally.
