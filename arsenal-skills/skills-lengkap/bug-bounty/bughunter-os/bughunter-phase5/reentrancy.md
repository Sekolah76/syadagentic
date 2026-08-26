# Reentrancy

Questions:
- Which invariant could be violated?
- Is storage updated before external calls?
- Can callbacks re-enter another function?
- Does cross-function reentrancy exist?
- Is profit possible or only DoS?

False positives:
- Read-only callbacks
- Proper CEI + effective guard
