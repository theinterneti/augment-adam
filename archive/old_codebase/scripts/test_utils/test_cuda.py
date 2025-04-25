#!/usr/bin/env python3
"""
Test CUDA Installation

This script tests if CUDA is properly installed and accessible.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_nvidia_smi():
    """Check if nvidia-smi is available and working."""
    print("Checking nvidia-smi...")
    success, output = run_command("nvidia-smi")
    if success:
        print("✅ nvidia-smi is working:")
        print(output)
        return True
    else:
        print("❌ nvidia-smi failed:")
        print(output)
        return False

def check_cuda_version():
    """Check CUDA version."""
    print("\nChecking CUDA version...")
    success, output = run_command("nvcc --version")
    if success:
        print("✅ NVCC is available:")
        print(output)
        return True
    else:
        print("❌ NVCC is not available. This is normal for runtime-only installations.")
        print("Checking for CUDA runtime libraries...")
        
        # Check for CUDA runtime libraries
        cuda_paths = [
            "/usr/local/cuda/lib64",
            "/usr/lib/x86_64-linux-gnu",
            "/usr/lib/cuda/lib64"
        ]
        
        cuda_libs_found = False
        for path in cuda_paths:
            if os.path.exists(path):
                libs = [f for f in os.listdir(path) if f.startswith("libcuda") or f.startswith("libcudart")]
                if libs:
                    print(f"✅ CUDA libraries found in {path}:")
                    for lib in libs:
                        print(f"  - {lib}")
                    cuda_libs_found = True
        
        if cuda_libs_found:
            return True
        else:
            print("❌ No CUDA libraries found in standard locations.")
            return False

def check_pytorch_cuda():
    """Check if PyTorch can access CUDA."""
    print("\nChecking PyTorch CUDA support...")
    try:
        import torch
        
        print(f"PyTorch version: {torch.__version__}")
        cuda_available = torch.cuda.is_available()
        print(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ CUDA device count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"✅ CUDA device {i} name: {torch.cuda.get_device_name(i)}")
                
            # Test a simple tensor operation on GPU
            print("\nRunning a simple tensor operation on GPU...")
            x = torch.rand(5, 3).cuda()
            y = torch.rand(5, 3).cuda()
            z = x + y
            print(f"✅ Tensor operation successful: {z.shape}")
            
            return True
        else:
            print("❌ PyTorch cannot access CUDA.")
            
            # Check why CUDA is not available
            print("\nDiagnosing why CUDA is not available...")
            
            # Check CUDA_VISIBLE_DEVICES
            cuda_visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "Not set")
            print(f"CUDA_VISIBLE_DEVICES: {cuda_visible_devices}")
            
            # Check if PyTorch was built with CUDA
            print(f"PyTorch CUDA compiled version: {torch.version.cuda}")
            
            return False
    except ImportError:
        print("❌ PyTorch is not installed.")
        return False
    except Exception as e:
        print(f"❌ Error checking PyTorch CUDA: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("CUDA INSTALLATION TEST")
    print("=" * 50)
    
    nvidia_smi_check = check_nvidia_smi()
    cuda_version_check = check_cuda_version()
    pytorch_cuda_check = check_pytorch_cuda()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"nvidia-smi working: {'✅' if nvidia_smi_check else '❌'}")
    print(f"CUDA libraries found: {'✅' if cuda_version_check else '❌'}")
    print(f"PyTorch CUDA support: {'✅' if pytorch_cuda_check else '❌'}")
    
    if nvidia_smi_check and (cuda_version_check or pytorch_cuda_check):
        print("\n✅ CUDA is properly installed and accessible.")
        return 0
    else:
        print("\n❌ There are issues with the CUDA installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
