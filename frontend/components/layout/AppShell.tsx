import { BottomNav } from "./BottomNav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-paper">
      <div className="mx-auto phone-shell">{children}</div>
      <BottomNav />
    </div>
  );
}
