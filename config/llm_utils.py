"""
LLM utilities for Real Estate AI
Provides model initialization, caching, and fallback mechanisms
"""

import os
import requests
import json
import subprocess
from typing import Optional, List, Dict, Any
from .logger import get_logger
from .config import FREE_LLM_ENDPOINTS, DEFAULT_MODEL, FALLBACK_MODE

logger = get_logger(__name__)

class LLMProvider:
    """Provider for LLM models with fallback options and caching"""
    
    def __init__(self):
        """Initialize the LLM provider"""
        self.logger = logger
        self.cache = {}
        self.free_endpoints = FREE_LLM_ENDPOINTS
        self.default_model = DEFAULT_MODEL
        self.fallback_mode = FALLBACK_MODE
        self.logger.info("Initializing LLM provider")
        
    def check_ollama_availability(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            if response.status_code == 200:
                self.logger.info("Ollama is available")
                return True
        except:
            pass
        
        self.logger.warning("Ollama is not available")
        return False
    
    def check_local_ai_availability(self) -> bool:
        """Check if LocalAI is running"""
        try:
            response = requests.get("http://localhost:8080/v1/models", timeout=2)
            if response.status_code == 200:
                self.logger.info("LocalAI is available")
                return True
        except:
            pass
            
        self.logger.warning("LocalAI is not available")
        return False
    
    def get_available_models(self) -> List[str]:
        """Get a list of available models"""
        models = []
        
        # Check for API keys first
        if os.getenv("OPENAI_API_KEY"):
            models.append("gpt-4o")
            models.append("gpt-3.5-turbo")
            
        if os.getenv("ANTHROPIC_API_KEY"):
            models.append("claude-3-opus")
            models.append("claude-3-sonnet")
        
        # Check for Ollama
        if self.check_ollama_availability():
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("models", []):
                        models.append(f"ollama/{model['name']}")
            except:
                pass
        
        # Check for LocalAI
        if self.check_local_ai_availability():
            try:
                response = requests.get("http://localhost:8080/v1/models")
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        models.append(f"localai/{model['id']}")
            except:
                pass
        
        # Always include fake LLM for demo mode
        models.append("fake")
        
        return models
    
    def ensure_ollama_model(self, model_name: str) -> bool:
        """Ensure an Ollama model is downloaded"""
        if not self.check_ollama_availability():
            return False
            
        try:
            # Check if model exists
            response = requests.get(f"http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    if model["name"] == model_name:
                        self.logger.info(f"Ollama model {model_name} is already available")
                        return True
            
            # If model doesn't exist, pull it
            self.logger.info(f"Pulling Ollama model {model_name}")
            pull_response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name}
            )
            
            if pull_response.status_code == 200:
                self.logger.info(f"Successfully pulled Ollama model {model_name}")
                return True
                
            self.logger.error(f"Failed to pull Ollama model {model_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error ensuring Ollama model: {str(e)}")
            return False
    
    def get_best_available_model(self) -> str:
        """Get the best available model based on what's installed"""
        available_models = self.get_available_models()
        
        # First try official API models if keys are available
        if os.getenv("ANTHROPIC_API_KEY") and "claude-3-sonnet" in available_models:
            return "claude-3-sonnet"
        if os.getenv("OPENAI_API_KEY") and "gpt-4o" in available_models:
            return "gpt-4o"
        
        # Then try local models
        for model in ["ollama/llama3", "ollama/mistral", "localai/gpt4all"]:
            if model in available_models:
                return model
        
        # Fallback to fake LLM for demo
        return "fake"
    
    def initialize_llm(self, model_name=None, temperature=0.2):
        """
        Initialize a language model with appropriate fallbacks
        
        Args:
            model_name: The name of the model to initialize
            temperature: The temperature for generation
            
        Returns:
            An initialized language model
        """
        from langchain.chains.base import Chain
        
        if model_name is None:
            model_name = self.get_best_available_model()
            
        self.logger.info(f"Initializing model: {model_name}")
        
        try:
            # Handle official API-based models
            if model_name == "gpt-4o" or model_name == "gpt-3.5-turbo":
                from langchain_openai import ChatOpenAI
                
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                    
                return ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    api_key=api_key
                )
                
            elif model_name.startswith("claude"):
                from langchain_anthropic import ChatAnthropic
                
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                    
                return ChatAnthropic(
                    model_name=model_name,
                    temperature=temperature,
                    api_key=api_key
                )
                
            # Handle Ollama models
            elif model_name.startswith("ollama/"):
                from langchain_community.llms import Ollama
                
                if not self.check_ollama_availability():
                    raise ValueError("Ollama is not available")
                
                # Extract the actual model name
                actual_model = model_name.split("/")[1]
                
                # Ensure model is downloaded
                if not self.ensure_ollama_model(actual_model):
                    raise ValueError(f"Could not ensure Ollama model: {actual_model}")
                
                return Ollama(model=actual_model, temperature=temperature)
                
            # Handle LocalAI models
            elif model_name.startswith("localai/"):
                from langchain_community.llms import LocalAI
                
                if not self.check_local_ai_availability():
                    raise ValueError("LocalAI is not available")
                
                # Extract the actual model name
                actual_model = model_name.split("/")[1]
                
                return LocalAI(model=actual_model, temperature=temperature, api_base="http://localhost:8080/v1")
                
            # Fallback to fake LLM
            elif model_name == "fake":
                from langchain.llms.fake import FakeListLLM
                
                responses = [
                    "I've analyzed the real estate data for all the target cities.",
                    "Based on my analysis, I've identified the top investment areas in each city.",
                    "The highest ROI potential is in tech hubs and areas with ongoing infrastructure development.",
                    "Here are my detailed recommendations for real estate investment across Indian metros."
                ]
                
                return FakeListLLM(responses=responses)
            
            else:
                raise ValueError(f"Unsupported model: {model_name}")
                
        except Exception as e:
            # Handle failure
            self.logger.error(f"Error initializing model {model_name}: {str(e)}")
            
            if self.fallback_mode:
                self.logger.warning(f"Falling back to demo mode")
                from langchain.llms.fake import FakeListLLM
                
                responses = [
                    "I've analyzed the real estate data for all the target cities.",
                    "Based on my analysis, I've identified the top investment areas in each city.",
                    "The highest ROI potential is in tech hubs and areas with ongoing infrastructure development.",
                    "Here are my detailed recommendations for real estate investment across Indian metros."
                ]
                
                return FakeListLLM(responses=responses)
            else:
                raise e