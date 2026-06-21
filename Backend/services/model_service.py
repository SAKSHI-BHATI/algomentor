class ModelService:

    def get_hints(self, problem):
        try:
            from AI_engine.model_logic.hint_generation_model import predict
            result = predict(problem)

            return {"success": True, "hints": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_next_step(self, thought):
        try:
            from AI_engine.model_logic.reasoning_next_step_model import predict
            result = predict(thought)

            return {"success": True, "next_step": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def evaluate_pseudocode(self,code):
        try:
            from AI_engine.model_logic.pseudocode_evaluation_model import predict
            result = predict(code)   # returns { "label": ... }
            label = result["label"]
            # 🔥 Add human-readable feedback
            if label == "brute_force":
                feedback = "This is a brute force approach. Try optimizing."
            elif label == "better":
                feedback = "This is an improved approach, but not optimal yet."
            elif label == "optimal":
                feedback = "Great! This is an optimal solution."
            else:
                feedback = "This solution seems incorrect. Review logic."
            return {
                "label": label,
                "feedback": feedback
            }
        except Exception as e:
            return {"error": str(e)}

    def evaluate_understanding(self, text, problem=""):
        try:
            from AI_engine.model_logic.understanding_model import predict as understanding_predict

            result = understanding_predict(text, problem=problem)
            decision = result["prediction"]
            if decision == "PROCEED":
                return {
                    "decision": "PROCEED",
                    "feedback": "Great start! Your approach looks correct."
                }
            else:
                return {
                    "decision": "WATCH",
                    "feedback": "Your approach needs improvement. Try reviewing the concept again."
                }
        except Exception as e:
            return {
                "decision": "WATCH",
                "feedback": f"Could not evaluate understanding. Error: {str(e)}"
            }

model_service = ModelService()