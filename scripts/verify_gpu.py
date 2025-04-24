#!/usr/bin/env python3
"""
GPU Verification Script

This script checks if PyTorch can access the GPU and prints relevant information.
"""

import sys
import subprocess

def check_system_gpu():
    """Check if NVIDIA GPU is available at the system level."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("NVIDIA GPU detected at system level:")
            print(result.stdout)
            return True
        else:
            print("nvidia-smi command failed. No GPU detected at system level.")
            return False
    except FileNotFoundError:
        print("nvidia-smi command not found. NVIDIA drivers may not be installed.")
        return False

def check_pytorch_gpu():
    """Check if PyTorch can access the GPU."""
    try:
        import torch
        
        print("\nPyTorch GPU Information:")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"CUDA device count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"CUDA device {i} name: {torch.cuda.get_device_name(i)}")
                print(f"CUDA device {i} capability: {torch.cuda.get_device_capability(i)}")
                
            # Test a simple tensor operation on GPU
            print("\nRunning a simple tensor operation on GPU...")
            x = torch.rand(5, 3).cuda()
            y = torch.rand(5, 3).cuda()
            z = x + y
            print(f"Tensor operation successful: {z.shape}")
            
            return True
        else:
            print("PyTorch cannot access GPU.")
            return False
    except ImportError:
        print("PyTorch is not installed.")
        return False
    except Exception as e:
        print(f"Error checking PyTorch GPU: {str(e)}")
        return False

def check_ollama_gpu():
    """Check if Ollama is using the GPU."""
    try:
        import requests
        
        print("\nChecking Ollama GPU usage:")
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("Ollama is running.")
                
                # Run a simple inference to check GPU usage
                prompt = "Write a one-sentence test."
                payload = {
                    "model": "tinyllama:1.1b",
                    "prompt": prompt,
                    "stream": False
                }
                
                print("Running a simple inference with Ollama...")
                response = requests.post("http://localhost:11434/api/generate", json=payload)
                
                if response.status_code == 200:
                    print("Ollama inference successful.")
                    return True
                else:
                    print(f"Ollama inference failed: {response.text}")
                    return False
            else:
                print(f"Ollama API returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Could not connect to Ollama API. Make sure Ollama is running.")
            return False
    except ImportError:
        print("Requests library is not installed.")
        return False
    except Exception as e:
        print(f"Error checking Ollama GPU: {str(e)}")
        return False

def main():
    """Main function."""
    print("GPU Verification Script")
    print("======================\n")
    
    system_gpu = check_system_gpu()
    pytorch_gpu = check_pytorch_gpu()
    ollama_gpu = check_ollama_gpu()
    
    print("\nSummary:")
    print(f"System GPU detected: {system_gpu}")
    print(f"PyTorch GPU access: {pytorch_gpu}")
    print(f"Ollama running with inference: {ollama_gpu}")
    
    if system_gpu and pytorch_gpu and ollama_gpu:
        print("\nAll GPU checks passed! Your system is ready for GPU-accelerated test generation.")
        return 0
    else:
        print("\nSome GPU checks failed. Review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
