export function Logo({
  light = false,
  size = 28,
  withWord = true,
}: {
  light?: boolean;
  size?: number;
  withWord?: boolean;
}) {
  const color = light ? "#F6F5F1" : "#0E4A38";
  return (
    <span className="inline-flex items-center gap-2">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
        <path
          d="M16 3.5c-5.1 0-9.2 4-9.2 9 0 6.6 8.1 15.2 8.5 15.6a1 1 0 0 0 1.4 0c.4-.4 8.5-9 8.5-15.6 0-5-4.1-9-9.2-9Z"
          fill={color}
        />
        <circle cx="16" cy="12.2" r="3.1" fill={light ? "#0A3328" : "#F6F5F1"} />
        <path
          d="M12.2 21.6c2.2 1.4 5.4 1.4 7.6 0"
          stroke={color}
          strokeWidth="1.4"
          fill="none"
          strokeLinecap="round"
        />
        <path
          d="M10.4 23.8c3.3 2.1 7.9 2.1 11.2 0"
          stroke={color}
          strokeWidth="1.4"
          fill="none"
          strokeLinecap="round"
          opacity="0.7"
        />
      </svg>
      {withWord ? (
        <span className={`text-[17px] font-semibold tracking-tight ${light ? "text-paper" : "text-forest"}`}>
          Signal
        </span>
      ) : (
        <span className="sr-only">Signal</span>
      )}
    </span>
  );
}
