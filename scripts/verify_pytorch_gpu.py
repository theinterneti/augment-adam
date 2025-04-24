#!/usr/bin/env python3
"""
Verify PyTorch GPU Support

This script checks if PyTorch can access the GPU and runs a simple test.
"""

import sys

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
            
            # Run a simple benchmark
            print("\nRunning a simple benchmark...")
            import time
            
            # Matrix multiplication benchmark
            size = 2000
            a = torch.randn(size, size).cuda()
            b = torch.randn(size, size).cuda()
            
            # Warm-up
            for _ in range(5):
                c = torch.matmul(a, b)
            
            # Benchmark
            torch.cuda.synchronize()
            start_time = time.time()
            iterations = 10
            
            for _ in range(iterations):
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"Matrix multiplication ({size}x{size}) benchmark:")
            print(f"Total time for {iterations} iterations: {elapsed_time:.4f} seconds")
            print(f"Average time per iteration: {elapsed_time/iterations:.4f} seconds")
            
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

def main():
    """Main function."""
    print("PyTorch GPU Verification")
    print("=======================\n")
    
    pytorch_gpu = check_pytorch_gpu()
    
    if pytorch_gpu:
        print("\nSuccess! PyTorch can access the GPU.")
        return 0
    else:
        print("\nFailed: PyTorch cannot access the GPU.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
