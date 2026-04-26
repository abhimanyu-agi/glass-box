import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * cn() — merges Tailwind classes intelligently.
 * Used everywhere in shadcn-style components.
 *   cn("px-2", "px-4") → "px-4"   (later wins)
 *   cn("px-2", isActive && "bg-blue-500") → conditional classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}