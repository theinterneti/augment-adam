"""Hugging Face Model implementation.

This module provides an implementation of the ModelInterface for Hugging Face models.

Version: 0.1.0
Created: 2025-04-28
"""

import logging
import os
import dotenv
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    AutoModelForSeq2SeqLM, pipeline,
    TextIteratorStreamer, BitsAndBytesConfig
)
from threading import Thread
import gc

# Load environment variables
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

from augment_adam.models.caching import get_model_cache

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
        use_auth_token: bool = True,
        use_cache: bool = True,
        max_cache_size: int = 1024 * 1024 * 1024,  # 1 GB
        context_window_size: Optional[int] = None,
        use_flash_attention: bool = True,
        use_bettertransformer: bool = True,
        **kwargs
    ):
        """Initialize the Hugging Face Model.

        Args:
            model_name: The name of the Hugging Face model to use
            device: The device to run the model on (if None, use CUDA if available)
            load_in_8bit: Whether to load the model in 8-bit precision
            load_in_4bit: Whether to load the model in 4-bit precision
            use_auth_token: Whether to use the Hugging Face token for authentication
            use_cache: Whether to use the model cache
            max_cache_size: Maximum cache size in bytes
            context_window_size: Size of the context window (if None, use model default)
            use_flash_attention: Whether to use Flash Attention for faster inference
            use_bettertransformer: Whether to use BetterTransformer for faster inference
            **kwargs: Additional parameters for model loading
        """
        try:
            self.model_name = model_name

            # Get Hugging Face token from environment
            self.hf_token = os.environ.get("HF_TOKEN")
            if use_auth_token and not self.hf_token:
                logger.warning("HF_TOKEN environment variable not found. Some models may not be accessible.")

            # Determine device
            if device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device

            # Initialize cache
            self.use_cache = use_cache
            if use_cache:
                self.cache = get_model_cache(
                    model_name=model_name,
                    provider="huggingface",
                    max_cache_size=max_cache_size
                )
            else:
                self.cache = None

            logger.info(f"Loading model {model_name} on {self.device}")
            if load_in_8bit:
                logger.info("Using 8-bit quantization")
            if load_in_4bit:
                logger.info("Using 4-bit quantization")

            # Set up quantization config
            quantization_config = None
            if load_in_4bit or load_in_8bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=load_in_4bit,
                    load_in_8bit=load_in_8bit,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )

            # Check if tokenizer is in cache
            tokenizer_path = None
            if self.cache:
                tokenizer_path = self.cache.get_tokenizer_path()

            # Load tokenizer
            if tokenizer_path:
                logger.info(f"Loading tokenizer from cache: {tokenizer_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    tokenizer_path,
                    token=self.hf_token if use_auth_token else None
                )
            else:
                logger.info("Loading tokenizer from Hugging Face")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=self.hf_token if use_auth_token else None
                )

                # Save tokenizer to cache
                if self.cache:
                    self.cache.save_tokenizer(self.tokenizer)

            # Set up model loading kwargs
            model_kwargs = {
                "device_map": self.device,
                "quantization_config": quantization_config,
                "token": self.hf_token if use_auth_token else None,
                **kwargs
            }

            # Add Flash Attention if requested and available
            if use_flash_attention and self.device == "cuda":
                try:
                    from transformers import AutoConfig
                    config = AutoConfig.from_pretrained(model_name)

                    # Check if model supports attention implementation
                    if hasattr(config, "attn_implementation"):
                        model_kwargs["attn_implementation"] = "flash_attention_2"
                        logger.info("Using Flash Attention 2")
                except Exception as e:
                    logger.warning(f"Failed to set up Flash Attention: {e}")

            # Set context window size if provided
            if context_window_size:
                model_kwargs["max_position_embeddings"] = context_window_size
                model_kwargs["rope_scaling"] = {"type": "dynamic", "factor": 2.0}
                logger.info(f"Setting context window size to {context_window_size}")

            # Check if model is in cache
            model_path = None
            if self.cache:
                model_path = self.cache.get_model_path()

            # Determine model type and load model
            try:
                # Try loading as a causal language model first
                if model_path:
                    logger.info(f"Loading causal model from cache: {model_path}")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        **model_kwargs
                    )
                else:
                    logger.info("Loading causal model from Hugging Face")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        **model_kwargs
                    )

                    # Save model to cache
                    if self.cache:
                        self.cache.save_model_weights(self.model)

                self.model_type = "causal"
            except Exception as e:
                logger.info(f"Failed to load as causal model, trying seq2seq: {e}")

                # Free up memory
                if 'self.model' in locals():
                    del self.model
                    gc.collect()
                    torch.cuda.empty_cache()

                # Try loading as a seq2seq model
                if model_path:
                    logger.info(f"Loading seq2seq model from cache: {model_path}")
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        model_path,
                        **model_kwargs
                    )
                else:
                    logger.info("Loading seq2seq model from Hugging Face")
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        model_name,
                        **model_kwargs
                    )

                    # Save model to cache
                    if self.cache:
                        self.cache.save_model_weights(self.model)

                self.model_type = "seq2seq"

            # Apply BetterTransformer if requested
            if use_bettertransformer:
                try:
                    from optimum.bettertransformer import BetterTransformer
                    self.model = BetterTransformer.transform(self.model)
                    logger.info("Applied BetterTransformer optimization")
                except Exception as e:
                    logger.warning(f"Failed to apply BetterTransformer: {e}")

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
                self.embedding_model = SentenceTransformer(
                    "all-MiniLM-L6-v2",
                    token=self.hf_token if use_auth_token else None
                )
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
        use_cache: Optional[bool] = None,
        use_monte_carlo: bool = True,
        monte_carlo_particles: int = 50,
        monte_carlo_potentials: Optional[List[Any]] = None,
        **kwargs
    ) -> str:
        """Generate text based on a prompt.

        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_p: Nucleus sampling parameter (1.0 = no nucleus sampling)
            stop: List of strings that stop generation when encountered
            use_cache: Whether to use the cache (if None, use the instance setting)
            use_monte_carlo: Whether to use Monte Carlo sampling
            monte_carlo_particles: Number of particles for Monte Carlo sampling
            monte_carlo_potentials: Potentials for Monte Carlo sampling
            **kwargs: Additional model-specific parameters

        Returns:
            The generated text
        """
        try:
            # Check if we should use the cache
            should_use_cache = self.use_cache if use_cache is None else use_cache

            # Create cache key parameters
            cache_params = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop,
                "use_monte_carlo": use_monte_carlo,
                "monte_carlo_particles": monte_carlo_particles,
                **kwargs
            }

            # Check if result is in cache
            if should_use_cache and self.cache:
                cached_result = self.cache.get_generation(prompt, cache_params)
                if cached_result:
                    logger.info(f"Using cached generation for {prompt[:20]}...")
                    return cached_result

            # If Monte Carlo sampling is requested and potentials are provided, use SMC
            if use_monte_carlo and monte_carlo_potentials:
                # Check if parallel processing is requested
                use_parallel = kwargs.get("use_parallel_monte_carlo", False)
                num_workers = kwargs.get("monte_carlo_workers", None)
                use_gpu = kwargs.get("use_gpu_monte_carlo", False) and self.device == "cuda"

                if use_parallel:
                    from augment_adam.ai_agent.smc.parallel_sampler import ParallelSequentialMonteCarlo

                    # Create parallel SMC sampler
                    smc_sampler = ParallelSequentialMonteCarlo(
                        num_particles=monte_carlo_particles,
                        potentials=monte_carlo_potentials,
                        model=self,
                        num_workers=num_workers,
                        use_gpu=use_gpu,
                        batch_size=kwargs.get("monte_carlo_batch_size", 10)
                    )

                    # Generate with parallel SMC
                    generated_text = smc_sampler.sample(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop=stop,
                        timeout=kwargs.get("monte_carlo_timeout", None)
                    )
                else:
                    from augment_adam.ai_agent.smc.sampler import SequentialMonteCarlo

                    # Create sequential SMC sampler
                    smc_sampler = SequentialMonteCarlo(
                        num_particles=monte_carlo_particles,
                        potentials=monte_carlo_potentials,
                        model=self
                    )

                    # Generate with sequential SMC
                    generated_text = smc_sampler.sample(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop=stop
                    )

                # Cache the result
                if should_use_cache and self.cache:
                    self.cache.save_generation(prompt, cache_params, generated_text)

                return generated_text

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

            # Cache the result
            if should_use_cache and self.cache:
                self.cache.save_generation(prompt, cache_params, generated_text)

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

    def get_embedding(self, text: str, use_cache: Optional[bool] = None) -> List[float]:
        """Get the embedding for a text.

        Args:
            text: The text to get an embedding for
            use_cache: Whether to use the cache (if None, use the instance setting)

        Returns:
            The embedding as a list of floats
        """
        try:
            if not self.has_embeddings:
                raise ResourceError(
                    message="Embeddings are not available for this model",
                    details={"model_name": self.model_name}
                )

            # Check if we should use the cache
            should_use_cache = self.use_cache if use_cache is None else use_cache

            # Check if embedding is in cache
            if should_use_cache and self.cache:
                cached_embedding = self.cache.get_embedding(text)
                if cached_embedding:
                    logger.info(f"Using cached embedding for {text[:20]}...")
                    return cached_embedding

            # Generate embedding
            embedding = self.embedding_model.encode(text)
            embedding_list = embedding.tolist()

            # Cache the embedding
            if should_use_cache and self.cache:
                self.cache.save_embedding(text, embedding_list)

            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding_list
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

    def get_token_probabilities(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_k: int = 50,
        **kwargs
    ) -> List[Tuple[str, float]]:
        """Get token probabilities for the next token.

        Args:
            prompt: The prompt to get probabilities for
            temperature: Sampling temperature (higher = more random)
            top_k: Number of top tokens to return
            **kwargs: Additional model-specific parameters

        Returns:
            List of (token, probability) tuples
        """
        try:
            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            # Get logits for the next token
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[0, -1, :]

            # Apply temperature
            if temperature > 0:
                logits = logits / temperature

            # Convert to probabilities
            probs = torch.softmax(logits, dim=0)

            # Get top-k token indices and probabilities
            top_k = min(top_k, probs.size(0))
            top_probs, top_indices = torch.topk(probs, top_k)

            # Convert to tokens and probabilities
            result = []
            for i, (index, prob) in enumerate(zip(top_indices, top_probs)):
                token = self.tokenizer.decode(index)
                result.append((token, prob.item()))

            return result
        except Exception as e:
            logger.warning(f"Error getting token probabilities: {e}")
            return [(" ", 1.0)]  # Return a default token with probability 1.0

    def batch_get_token_probabilities(
        self,
        prompts: List[str],
        temperature: float = 0.7,
        top_k: int = 50,
        **kwargs
    ) -> List[List[str]]:
        """Get token probabilities for multiple prompts in batch.

        Args:
            prompts: List of prompts to get probabilities for
            temperature: Sampling temperature (higher = more random)
            top_k: Number of top tokens to return
            **kwargs: Additional model-specific parameters

        Returns:
            List of lists of candidate tokens
        """
        try:
            # Tokenize all prompts
            batch_inputs = self.tokenizer(prompts, padding=True, return_tensors="pt").to(self.device)

            # Get logits for the next token for all prompts
            with torch.no_grad():
                outputs = self.model(**batch_inputs)
                batch_logits = outputs.logits

            # Process each prompt's logits
            results = []

            for i, logits in enumerate(batch_logits):
                # Get the last token's logits
                last_token_logits = logits[-1, :]

                # Apply temperature
                if temperature > 0:
                    last_token_logits = last_token_logits / temperature

                # Convert to probabilities
                probs = torch.softmax(last_token_logits, dim=0)

                # Get top-k token indices and probabilities
                top_k_val = min(top_k, probs.size(0))
                top_probs, top_indices = torch.topk(probs, top_k_val)

                # Convert to tokens
                tokens = []
                for index in top_indices:
                    token = self.tokenizer.decode(index)
                    tokens.append(token)

                results.append(tokens)

            return results
        except Exception as e:
            logger.warning(f"Error in batch token probabilities: {e}")
            # Return default tokens
            return [[" "] * top_k for _ in range(len(prompts))]

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
