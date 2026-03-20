# Binary Dialect Classifier (Honduras vs Other) - Training Report

## Dataset Statistics
- Target representation: Downsampled to 50/50 balance (Total 2732 records)
- Train size: 2185
- Validation size: 273
- Test size: 274

## Training Metrics
- Runtime: 465.36s
- Epochs completed: 3

## Test Evaluation
- Accuracy: 0.9343
- F1 Score: 0.9343
- Precision: 0.9351
- Recall: 0.9343

## Confusion Matrix (Test Set)
| True \ Predicted | Other (0) | Honduras (1) |
|---|---|---|
| **Other (0)** | 125 | 12 |
| **Honduras (1)** | 6 | 131 |

## Required Inference Tests
1. **Input**: 'Vos sos maje si pensás eso'
   - **Prediction**: Other (Confidence: 0.8696)
2. **Input**: 'Qué onda wey'
   - **Prediction**: Other (Confidence: 0.9976)

## Model Status
The binary dialect classifier is built and safely exported to `models/honduras_dialect_binary_classifier/`.