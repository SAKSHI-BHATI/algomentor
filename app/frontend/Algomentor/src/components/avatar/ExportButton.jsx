import { useThree } from "@react-three/fiber";

export default function ExportButton() {
  const { gl, scene, camera } = useThree();

  const exportImage = () => {
    // Force render
    gl.render(scene, camera);

    // Get image from canvas
    const dataURL = gl.domElement.toDataURL("image/png");

    // Create download link
    const link = document.createElement("a");
    link.href = dataURL;
    link.download = "algo-mentor-avatar.png";
    link.click();
  };

  return (
    <button
      onClick={exportImage}
      className="mt-6 w-full py-3 rounded-2xl bg-gradient-to-r 
                 from-slate-900 to-indigo-600 text-white 
                 font-medium shadow-lg hover:scale-[1.02] 
                 transition-all duration-200"
    >
      Export as PNG
    </button>
  );
}