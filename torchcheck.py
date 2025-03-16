import torch

# Verify MPS support
if torch.backends.mps.is_available():
    mps_device = torch.device("mps")
    print("M1 GPU is available and PyTorch is configured to use MPS!")
else:
    print("MPS backend is not available. Check your setup.")
