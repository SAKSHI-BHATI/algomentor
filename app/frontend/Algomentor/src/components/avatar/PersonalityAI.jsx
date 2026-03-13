import { useAvatar } from "../../context/AvatarContext";

const personalities = {
  analytical: {
    outfit: "academic",
    hairColor: "#1e293b",
    accessory: "glasses",
  },
  creative: {
    outfit: "hoodie",
    hairColor: "#9333ea",
    accessory: "none",
  },
};

export default function PersonalityAI() {
  const { avatar, setAvatar } = useAvatar();

  const applyPersonality = (type) => {
    setAvatar({ ...avatar, ...personalities[type] });
  };

  return (
    <div className="mt-6">
      <h3 className="font-semibold mb-2">AI Suggest</h3>
      <button
        onClick={() => applyPersonality("analytical")}
        className="px-4 py-2 bg-slate-900 text-white rounded-xl mr-3"
      >
        Analytical
      </button>
      <button
        onClick={() => applyPersonality("creative")}
        className="px-4 py-2 bg-indigo-600 text-white rounded-xl"
      >
        Creative
      </button>
    </div>
  );
}