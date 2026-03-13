import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useAvatar } from "../../context/AvatarContext";

export default function AvatarModel() {
  const group = useRef();
  const { avatar } = useAvatar();

  useFrame((state) => {
  if (!group.current) return;

  group.current.position.y =
    Math.sin(state.clock.getElapsedTime()) * 0.05;
  });

  return (
    <group ref={group}>
      {/* Head */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshStandardMaterial color={avatar.skin} />
      </mesh>

      {/* Body */}
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[1.5, 2, 0.8]} />
        <meshStandardMaterial
          color={
            avatar.outfit === "academic"
              ? "#1e293b"
              : avatar.outfit === "hoodie"
              ? "#6366f1"
              : "#0f172a"
          }
        />
      </mesh>

      {/* Hair */}
      {avatar.hairStyle !== "none" && (
        <mesh position={[0, 2.2, 0]}>
          <boxGeometry args={[1.6, 0.5, 1.6]} />
          <meshStandardMaterial color={avatar.hairColor} />
        </mesh>
      )}

      {/* Glasses */}
      {avatar.accessory === "glasses" && (
        <mesh position={[0, 1.5, 0.8]}>
          <torusGeometry args={[0.4, 0.05, 16, 100]} />
          <meshStandardMaterial color="black" />
        </mesh>
      )}
    </group>
  );
}