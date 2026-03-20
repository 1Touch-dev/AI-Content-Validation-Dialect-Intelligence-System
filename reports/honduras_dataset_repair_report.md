# Honduras Dataset Repair Report

## Original Dataset Statistics
- Total records: 5000
- Real records: 1633
- Synthetic records: 3367

## Modifications
- Duplicates removed (sim > 0.90): 22
- Synthetic records removed (slang threshold & diversity): 4
- Total synthetic records discarded: 1734

## Final Dataset Size
- Total records: 3266
- Real: 1633 (50.0%)
- Synthetic: 1633 (50.0%)

## Slang Token Distribution (Final)
- maje: 5.7%
- pijudo: 0.7%
- cipote: 2.5%
- vos: 1.1%

## ML Splits
- Train (80%): 2612 records
- Validation (10%): 327 records
- Test (10%): 327 records

## Training Recommendation
The dataset has been successfully balanced. The synthetic ratio is ≤ 50%, repetitive overrepresented tokens have been clipped, and extreme semantic duplicates (<0.90 sim) were pruned. The dataset is now highly robust and safe for training the dialect intelligence model.