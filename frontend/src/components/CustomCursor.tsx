import React, { useEffect, useState } from 'react';

export const CustomCursor: React.FC = () => {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [trailingPos, setTrailingPos] = useState({ x: -100, y: -100 });
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseDown = () => setIsClicked(true);
    const handleMouseUp = () => setIsClicked(false);

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.tagName === 'INPUT' ||
        target.closest('button') ||
        target.closest('a')
      ) {
        setIsHovered(true);
      } else {
        setIsHovered(false);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('mouseover', handleMouseOver);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('mouseover', handleMouseOver);
    };
  }, []);

  useEffect(() => {
    const follow = requestAnimationFrame(() => {
      setTrailingPos((prev) => ({
        x: prev.x + (position.x - prev.x) * 0.25,
        y: prev.y + (position.y - prev.y) * 0.25,
      }));
    });
    return () => cancelAnimationFrame(follow);
  }, [position, trailingPos]);

  return (
    <div className="pointer-events-none fixed inset-0 z-[9999] overflow-hidden hidden sm:block">
      {/* Outer Comic Pop Ring */}
      <div
        className={`fixed rounded-full border-2 border-black transition-all duration-75 ease-out -translate-x-1/2 -translate-y-1/2 ${
          isHovered
            ? 'w-14 h-14 bg-yellow-400 border-black shadow-[4px_4px_0px_#000]'
            : isClicked
            ? 'w-6 h-6 bg-red-500 border-black'
            : 'w-10 h-10 bg-cyan-400/80 border-black shadow-[3px_3px_0px_#000]'
        }`}
        style={{
          left: `${trailingPos.x}px`,
          top: `${trailingPos.y}px`,
        }}
      />

      {/* Inner Comic Target Point */}
      <div
        className={`fixed w-3 h-3 rounded-full bg-red-600 border-2 border-black -translate-x-1/2 -translate-y-1/2 shadow-[2px_2px_0px_#000] ${
          isHovered ? 'scale-125 bg-black border-yellow-400' : ''
        }`}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
        }}
      />
    </div>
  );
};
