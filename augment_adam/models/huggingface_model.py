"""Hugging Face Model implementation.

This module provides an implementation of the ModelInterface for Hugging Face models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, 
    AutoModelForSeq2SeqLM, pipeline,
    TextIteratorStreamer
)
from threading import Thread

from augment_adam.core.errors import (
    ResourceError, NetworkError, wrap_error, log_error, ErrorCategory
)
from augment_adam.models.model_interface import ModelInterface

logger = logging.getLogger(__name__)


class HuggingFaceModel(ModelInterface):
    """Hugging Face Model implementation.
    
    This class provides an implementation of the ModelInterface for Hugging Face models.
    
    Attributes:
        model_name: The name of the Hugging Face model to use
        model: The loaded model
        tokenizer: The tokenizer for the model
        device: The device to run the model on
        model_type: The type of model (causal or seq2seq)
    """
    
    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        device: str = None,
        load_in_8bit: bool = False,
        load_in_4bit: bool = True,
        **kwargs
    ):
        """Initialize the Hugging Face Model.
        
        Args:
            model_name: The name of the Hugging Face model to use
            device: The device to run the model on (if None, use CUDA if available)
            load_in_8bit: Whether to load the model in 8-bit precision
            load_in_4bit: Whether to load the model in 4-bit precision
            **kwargs: Additional parameters for model loading
        """
        try:
            self.model_name = model_name
            
            # Determine device
            if device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Determine model type and load model
            try:
                # Try loading as a causal language model first
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map=self.device,
                    load_in_8bit=load_in_8bit,
                    load_in_4bit=load_in_4bit,
                    **kwargs
                )
                self.model_type = "causal"
            except Exception as e:
                logger.info(f"Failed to load as causal model, trying seq2seq: {e}")
                # Try loading as a seq2seq model
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    device_map=self.device,
                    load_in_8bit=load_in_8bit,
                    load_in_4bit=load_in_4bit,
                    **kwargs
                )
                self.model_type = "seq2seq"
            
            # Create generation pipeline
            self.pipeline = pipeline(
                "text-generation" if self.model_type == "causal" else "text2text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            # Create embedding pipeline if available
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.has_embeddings = True
            except (ImportError, Exception) as e:
                logger.warning(f"Sentence transformers not available, embeddings will be disabled: {e}")
                self.has_embeddings = False
            
            logger.info(f"Initialized Hugging Face Model: {model_name} on {self.device}")
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to initialize Hugging Face Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": model_name}
            )
            log_error(error, logger=logger)
            raise error
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Generate text based on a prompt.
        
        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling)
            stop: List of strings that stop generation when encountered
            **kwargs: Additional model-specific parameters
            
        Returns:
            The generated text
        """
        try:
            # Format prompt based on model type
            formatted_prompt = self._format_prompt(prompt)
            
            # Set generation parameters
            generation_kwargs = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": temperature > 0,
                "pad_token_id": self.tokenizer.eos_token_id,
                **kwargs
            }
            
            # Add stop sequences if provided
            if stop:
                generation_kwargs["stopping_criteria"] = self._create_stopping_criteria(stop)
            
            # Generate text
            outputs = self.pipeline(
                formatted_prompt,
                **generation_kwargs
            )
            
            # Extract generated text
            if self.model_type == "causal":
                generated_text = outputs[0]["generated_text"]
                # Remove the prompt from the beginning if it's there
                if generated_text.startswith(formatted_prompt):
                    generated_text = generated_text[len(formatted_prompt):]
            else:
                generated_text = outputs[0]["generated_text"]
            
            logger.info(f"Generated {len(generated_text)} characters with {self.model_name}")
            return generated_text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate text with Hugging Face Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            return f"Error generating text: {str(error)}"
    
    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Generate text based on a prompt, streaming the results.
        
        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling)
            stop: List of strings that stop generation when encountered
            **kwargs: Additional model-specific parameters
            
        Returns:
            A generator yielding chunks of generated text
        """
        try:
            # Format prompt based on model type
            formatted_prompt = self._format_prompt(prompt)
            
            # Create streamer
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)
            
            # Set generation parameters
            generation_kwargs = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": temperature > 0,
                "pad_token_id": self.tokenizer.eos_token_id,
                "streamer": streamer,
                **kwargs
            }
            
            # Add stop sequences if provided
            if stop:
                generation_kwargs["stopping_criteria"] = self._create_stopping_criteria(stop)
            
            # Tokenize input
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
            
            # Start generation in a separate thread
            thread = Thread(target=self._generate_thread, args=(inputs, generation_kwargs))
            thread.start()
            
            # Yield from streamer
            for text in streamer:
                yield text
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to stream text with Hugging Face Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            yield f"Error generating text: {str(error)}"
    
    def _generate_thread(self, inputs, generation_kwargs):
        """Generate text in a separate thread.
        
        Args:
            inputs: Tokenized inputs
            generation_kwargs: Generation parameters
        """
        try:
            self.model.generate(**inputs, **generation_kwargs)
        except Exception as e:
            logger.error(f"Error in generation thread: {e}")
    
    def _format_prompt(self, prompt: str) -> str:
        """Format the prompt based on the model type.
        
        Args:
            prompt: The prompt to format
            
        Returns:
            The formatted prompt
        """
        # Check if the model is an instruction-tuned model
        if "instruct" in self.model_name.lower() or "chat" in self.model_name.lower():
            # Format for instruction-tuned models
            if "mistral" in self.model_name.lower():
                return f"<s>[INST] {prompt} [/INST]"
            elif "llama" in self.model_name.lower():
                return f"<s>[INST] {prompt} [/INST]"
            elif "falcon" in self.model_name.lower():
                return f"User: {prompt}\nAssistant:"
            else:
                return f"### Instruction:\n{prompt}\n\n### Response:"
        else:
            # For non-instruction models, just return the prompt
            return prompt
    
    def _create_stopping_criteria(self, stop_sequences: List[str]):
        """Create stopping criteria for generation.
        
        Args:
            stop_sequences: List of sequences that stop generation
            
        Returns:
            Stopping criteria for generation
        """
        from transformers import StoppingCriteria, StoppingCriteriaList
        
        class StopSequenceCriteria(StoppingCriteria):
            def __init__(self, tokenizer, stop_sequences, prompt_length):
                self.tokenizer = tokenizer
                self.stop_sequences = stop_sequences
                self.prompt_length = prompt_length
            
            def __call__(self, input_ids, scores, **kwargs):
                # Get the generated text
                generated_text = self.tokenizer.decode(input_ids[0][self.prompt_length:])
                # Check if any stop sequence is in the generated text
                return any(seq in generated_text for seq in self.stop_sequences)
        
        # Get the token IDs for the prompt
        prompt_ids = self.tokenizer.encode(self._format_prompt(""), return_tensors="pt")
        prompt_length = prompt_ids.shape[1]
        
        # Create stopping criteria
        stopping_criteria = StoppingCriteriaList([
            StopSequenceCriteria(self.tokenizer, stop_sequences, prompt_length)
        ])
        
        return stopping_criteria
    
    def get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens
        """
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to count tokens with Hugging Face Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            
            # Fall back to a simple approximation
            return len(text.split()) * 4 // 3  # Rough approximation
    
    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding for a text.
        
        Args:
            text: The text to get an embedding for
            
        Returns:
            The embedding as a list of floats
        """
        try:
            if not self.has_embeddings:
                raise ResourceError(
                    message="Embeddings are not available for this model",
                    details={"model_name": self.model_name}
                )
            
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding.tolist()
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get embedding with Hugging Face Model",
                category=ErrorCategory.RESOURCE,
                details={"model_name": self.model_name}
            )
            log_error(error, logger=logger)
            
            # Return a zero vector as fallback
            return [0.0] * 384  # Default embedding size for all-MiniLM-L6-v2
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model.
        
        Returns:
            A dictionary containing model information
        """
        # Get model configuration
        config = self.model.config.to_dict()
        
        return {
            "name": self.model_name,
            "provider": "Hugging Face",
            "type": self.model_type,
            "device": self.device,
            "max_tokens": config.get("max_position_embeddings", 2048),
            "embedding_dimensions": 384 if self.has_embeddings else None,
            "vocab_size": config.get("vocab_size", None),
            "hidden_size": config.get("hidden_size", None)
        }
