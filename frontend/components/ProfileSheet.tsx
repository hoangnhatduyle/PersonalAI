"use client";

import { useEffect, useRef } from "react";
import ProfileCard from "./ProfileCard";

interface Props {
  topic: string;
  topicColor: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ProfileSheet({ topic, topicColor, isOpen, onClose }: Props) {
  const sheetRef = useRef<HTMLDivElement>(null);

  // Lock body scroll when open
  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  // Swipe-down to close
  useEffect(() => {
    const el = sheetRef.current;
    if (!el) return;

    let startY = 0;
    const onTouchStart = (e: TouchEvent) => { startY = e.touches[0].clientY; };
    const onTouchEnd   = (e: TouchEvent) => {
      if (e.changedTouches[0].clientY - startY > 60) onClose();
    };

    el.addEventListener("touchstart", onTouchStart, { passive: true });
    el.addEventListener("touchend",   onTouchEnd,   { passive: true });
    return () => {
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchend",   onTouchEnd);
    };
  }, [onClose]);

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        className={`fixed inset-0 z-40 lg:hidden bg-black/60 backdrop-blur-sm
                    transition-opacity duration-300
                    ${isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}`}
      />

      {/* Sheet panel */}
      <div
        ref={sheetRef}
        className={`fixed bottom-0 left-0 right-0 z-50 lg:hidden
                    bg-zinc-900 border-t border-zinc-700/80 rounded-t-2xl
                    flex flex-col max-h-[82vh]
                    transition-transform duration-300 ease-out
                    ${isOpen ? "translate-y-0" : "translate-y-full"}`}
      >
        {/* Drag handle + header */}
        <div className="flex-shrink-0 flex flex-col items-center pt-3 pb-2 border-b border-zinc-800">
          <div className="w-10 h-1 bg-zinc-600 rounded-full mb-3" />
          <div className="flex items-center gap-2 px-4 pb-1 w-full">
            <div className={`w-6 h-6 rounded-full ${topicColor} flex items-center justify-center text-[10px] font-bold text-white transition-colors duration-500`}>
              HL
            </div>
            <p className="text-sm font-semibold text-white">Hoang&apos;s Profile</p>
            <button
              onClick={onClose}
              className="ml-auto text-zinc-500 hover:text-zinc-300 transition-colors p-1"
              aria-label="Close"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Scrollable card content */}
        <div className="flex-1 overflow-y-auto">
          <ProfileCard topic={topic} />
        </div>
      </div>
    </>
  );
}
