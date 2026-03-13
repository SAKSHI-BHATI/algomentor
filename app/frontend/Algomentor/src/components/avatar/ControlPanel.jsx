import { useAvatar } from "../../context/AvatarContext";

export default function ControlPanel() {
  const { avatar, setAvatar } = useAvatar();

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 space-y-6">
      <h2 className="text-xl font-semibold text-slate-800">
        Customize Avatar
      </h2>

      <div>
        <label className="block text-sm font-medium">Skin Tone</label>
        <input
          type="color"
          value={avatar.skin}
          onChange={(e) =>
            setAvatar({ ...avatar, skin: e.target.value })
          }
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Hair Color</label>
        <input
          type="color"
          value={avatar.hairColor}
          onChange={(e) =>
            setAvatar({ ...avatar, hairColor: e.target.value })
          }
        />
      </div>
    </div>
  );
}