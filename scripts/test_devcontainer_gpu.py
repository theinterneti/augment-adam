#!/usr/bin/env python3
"""
Test script to verify GPU support in the devcontainer.
"""

import subprocess
import sys

def check_system_gpu():
    """Check if NVIDIA GPU is available at the system level."""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected at system level:")
            print(result.stdout)
            return True
        else:
            print("❌ nvidia-smi command failed. No GPU detected at system level.")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi command not found. NVIDIA drivers may not be installed.")
        return False

def check_cuda_libraries():
    """Check if CUDA libraries are installed."""
    try:
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        if "libcuda.so" in result.stdout:
            print("✅ CUDA libraries found in system path.")
            return True
        else:
            print("❌ CUDA libraries not found in system path.")
            return False
    except FileNotFoundError:
        print("❌ ldconfig command not found. Cannot check CUDA libraries.")
        return False

def check_pytorch_gpu():
    """Check if PyTorch can access the GPU."""
    try:
        import torch
        
        print("\nPyTorch GPU Information:")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ CUDA device count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"✅ CUDA device {i} name: {torch.cuda.get_device_name(i)}")
                print(f"✅ CUDA device {i} capability: {torch.cuda.get_device_capability(i)}")
                
            # Test a simple tensor operation on GPU
            print("\nRunning a simple tensor operation on GPU...")
            x = torch.rand(5, 3).cuda()
            y = torch.rand(5, 3).cuda()
            z = x + y
            print(f"✅ Tensor operation successful: {z.shape}")
            
            return True
        else:
            print("❌ PyTorch cannot access GPU.")
            return False
    except ImportError:
        print("❌ PyTorch is not installed.")
        return False
    except Exception as e:
        print(f"❌ Error checking PyTorch GPU: {str(e)}")
        return False

def check_docker_gpu():
    """Check if Docker can access the GPU from within the container."""
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:12.0.0-base-ubuntu22.04", "nvidia-smi"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Docker can access the GPU:")
            print(result.stdout)
            return True
        else:
            print("❌ Docker cannot access the GPU:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ Docker command not found.")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker GPU access: {str(e)}")
        return False

def check_ollama():
    """Check if Ollama is installed and can be started."""
    try:
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed at:", result.stdout.strip())
            
            # Check if Ollama is running
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Ollama is running and responding to API calls.")
                return True
            else:
                print("❌ Ollama is installed but not running or not responding to API calls.")
                return False
        else:
            print("❌ Ollama is not installed.")
            return False
    except FileNotFoundError:
        print("❌ Required commands not found.")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("DEVCONTAINER GPU SUPPORT TEST")
    print("=" * 50)
    print("\nThis script checks if the devcontainer is correctly configured for GPU support.\n")
    
    system_gpu = check_system_gpu()
    cuda_libraries = check_cuda_libraries()
    pytorch_gpu = check_pytorch_gpu()
    docker_gpu = check_docker_gpu()
    ollama_check = check_ollama()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"System GPU detected: {'✅' if system_gpu else '❌'}")
    print(f"CUDA libraries installed: {'✅' if cuda_libraries else '❌'}")
    print(f"PyTorch GPU access: {'✅' if pytorch_gpu else '❌'}")
    print(f"Docker GPU access: {'✅' if docker_gpu else '❌'}")
    print(f"Ollama installed and running: {'✅' if ollama_check else '❌'}")
    
    success_count = sum([system_gpu, cuda_libraries, pytorch_gpu, docker_gpu, ollama_check])
    total_checks = 5
    
    print(f"\nPassed {success_count}/{total_checks} checks")
    
    if success_count == total_checks:
        print("\n✅ All checks passed! Your devcontainer is correctly configured for GPU support.")
        return 0
    else:
        print("\n⚠️ Some checks failed. Review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
