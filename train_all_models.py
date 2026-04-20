from AI_engine.model_logic.understanding_model import train_model as train_understanding
from AI_engine.model_logic.pseudocode_evaluation_model import train_model as train_pseudo

print("Training understanding model...")
train_understanding("Datasets/understanding_dataset.json")

print("Training pseudocode model...")
train_pseudo("Datasets/Pseudocode_Evaluation_Dataset.json")

print("Done ✅")