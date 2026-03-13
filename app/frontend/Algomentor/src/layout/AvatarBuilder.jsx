import { AvatarProvider } from "../context/AvatarContext";
import AvatarCanvas from "../components/avatar/AvatarCanvas";
import ControlPanel from "../components/avatar/ControlPanel";
import PersonalityAI from "../components/avatar/PersonalityAI";

export default function AvatarBuilder({ previewOnly, controlsOnly }) {
  return (
    <AvatarProvider>

      {/* PREVIEW ONLY */}
      {!controlsOnly && (
        <div className="w-full h-full flex items-center justify-center">
          <AvatarCanvas />
        </div>
      )}

      {/* CONTROLS ONLY */}
      {!previewOnly && (
        <div className="space-y-6">
          <ControlPanel />
          <PersonalityAI />
        </div>
      )}

    </AvatarProvider>
  );
}