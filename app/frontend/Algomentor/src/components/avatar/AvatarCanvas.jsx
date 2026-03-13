import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import AvatarModel from "./AvatarModel";

export default function AvatarCanvas() {
  return (
    <div className="h-[500px] w-full min-h-[500px] rounded-2xl shadow-xl bg-gradient-to-br from-slate-50 to-slate-200">
      <Canvas camera={{ position: [0, 1.5, 4], fov: 50 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[2, 5, 5]} intensity={1} />
        <AvatarModel />
        <OrbitControls enablePan={false} />
      </Canvas>
    </div>
  );
}