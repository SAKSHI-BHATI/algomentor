// StarBackground.jsx — AlgoMentor
// Renders 55 randomly positioned twinkling stars as a purely decorative
// background layer.  Sits behind all content via z-index:0 / pointerEvents:none.
// No external dependencies. No impact on layout or existing styles.

import React, { useMemo } from 'react';

// One shared <style> block injected once.
const KEYFRAMES = `
@keyframes am-star-twinkle-a {
  0%,100% { opacity: 0.08; transform: scale(0.7); }
  50%      { opacity: 0.75; transform: scale(1.25); }
}
@keyframes am-star-twinkle-b {
  0%,100% { opacity: 0.55; transform: scale(1); }
  40%     { opacity: 0.12; transform: scale(0.6); }
}
@keyframes am-star-twinkle-c {
  0%,33%  { opacity: 0.15; transform: scale(0.8); }
  66%     { opacity: 0.9;  transform: scale(1.3); }
  100%    { opacity: 0.15; transform: scale(0.8); }
}
`;

// Deterministic seeded pseudo-random so stars don't jump on re-renders
function seededRand(seed) {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

const ANIMATIONS = ["am-star-twinkle-a", "am-star-twinkle-b", "am-star-twinkle-c"];

const StarBackground = () => {
  const stars = useMemo(() => {
    const rand = seededRand(42);
    return Array.from({ length: 55 }, (_, i) => ({
      id:        i,
      top:       `${rand() * 100}%`,
      left:      `${rand() * 100}%`,
      size:      rand() * 2.2 + 0.8,          // 0.8 – 3 px
      anim:      ANIMATIONS[i % 3],
      duration:  `${rand() * 3.5 + 1.8}s`,   // 1.8 – 5.3 s
      delay:     `${rand() * 5}s`,            // 0 – 5 s offset
    }));
  }, []);

  return (
    <>
      {/* Keyframes injected once — prefixed name avoids any global collisions */}
      <style>{KEYFRAMES}</style>

      <div
        aria-hidden="true"
        style={{
          position:      "absolute",
          inset:         0,
          overflow:      "hidden",
          pointerEvents: "none",
          zIndex:        0,           // sits behind z-index:10 content in left panel
        }}
      >
        {stars.map((star) => (
          <div
            key={star.id}
            style={{
              position:     "absolute",
              top:          star.top,
              left:         star.left,
              width:        `${star.size}px`,
              height:       `${star.size}px`,
              borderRadius: "50%",
              background:   "#ffffff",
              animation:    `${star.anim} ${star.duration} ${star.delay} infinite ease-in-out`,
              pointerEvents:"none",
            }}
          />
        ))}
      </div>
    </>
  );
};

export default StarBackground;
