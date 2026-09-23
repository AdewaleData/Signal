"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/home", label: "Home", icon: HomeIcon },
  { href: "/routes", label: "Routes", icon: RoutesIcon },
  { href: "/reports", label: "Reports", icon: ReportsIcon },
  { href: "/profile", label: "Profile", icon: ProfileIcon },
];

export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-30 border-t border-line bg-white/95 backdrop-blur-sm"
      aria-label="Primary"
    >
      <div className="mx-auto flex max-w-[430px] items-stretch justify-between px-2 pb-[env(safe-area-inset-bottom)] lg:max-w-[1120px]">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex min-h-14 flex-1 flex-col items-center justify-center gap-1 text-[11px] ${
                active ? "text-forest" : "text-muted"
              }`}
              aria-current={active ? "page" : undefined}
            >
              <Icon active={active} />
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

function HomeIcon({ active }: { active: boolean }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 11.2 12 4l8 7.2V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.8Z"
        stroke={active ? "#0E4A38" : "#5C6B64"}
        strokeWidth="1.7"
        fill={active ? "#0E4A38" : "none"}
      />
    </svg>
  );
}

function RoutesIcon({ active }: { active: boolean }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M7 19V5m0 0 3 3M7 5 4 8m13 0v14m0 0 3-3m-3 3-3-3"
        stroke={active ? "#0E4A38" : "#5C6B64"}
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ReportsIcon({ active }: { active: boolean }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M7 4h8l4 4v12a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z"
        stroke={active ? "#0E4A38" : "#5C6B64"}
        strokeWidth="1.7"
      />
      <path d="M15 4v4h4M8 12h8M8 16h6" stroke={active ? "#0E4A38" : "#5C6B64"} strokeWidth="1.7" />
    </svg>
  );
}

function ProfileIcon({ active }: { active: boolean }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="3.2" stroke={active ? "#0E4A38" : "#5C6B64"} strokeWidth="1.7" />
      <path
        d="M5 19.2c.8-3 3.4-4.7 7-4.7s6.2 1.7 7 4.7"
        stroke={active ? "#0E4A38" : "#5C6B64"}
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}
