# Account Prospecting Agent Release Notes

## 1.1.0

### Highlights
- Simplified the runtime to the active on-device NPU pipeline using `phi-npu.exe` with keyword fallback.
- Removed the unused Genie/QAIRT-specific execution paths and cleaned up runtime initialization.
- Added architecture-specific PyInstaller packaging specs for x64 and x86.
- Produced signed Store-ready MSIX packages for x64 and x86.

### Packaging
- x64 package: `dist/AccountProspecting-1.1.0.0-x64.msix`
- x86 package: `dist/AccountProspecting-1.1.0.0-x86.msix`
- Exported signing certificates: `dist/AccountProspecting-x64.cer`, `dist/AccountProspecting-x86.cer`

### Notes
- Generated packaging intermediates are ignored by git.
- The app continues to use local device AI inference with the on-device NPU path as the primary processing flow.
