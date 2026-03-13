import { createContext, useContext, useEffect, useState } from "react";

const AvatarContext = createContext();

export const AvatarProvider = ({ children }) => {
  const [avatar, setAvatar] = useState(() => {
    const saved = localStorage.getItem("algo-avatar");
    return saved
      ? JSON.parse(saved)
      : {
          skin: "#f1c27d",
          hairStyle: "short",
          hairColor: "#2c2c2c",
          eyes: "normal",
          outfit: "academic",
          accessory: "none",
        };
  });

  useEffect(() => {
    localStorage.setItem("algo-avatar", JSON.stringify(avatar));
  }, [avatar]);

  return (
    <AvatarContext.Provider value={{ avatar, setAvatar }}>
      {children}
    </AvatarContext.Provider>
  );
};

export const useAvatar = () => {
  const context = useContext(AvatarContext);

  if (!context) {
    throw new Error("useAvatar must be used inside AvatarProvider");
  }

  return context;
};