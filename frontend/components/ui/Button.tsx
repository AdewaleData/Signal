import Link from "next/link";

type Props = {
  children: React.ReactNode;
  href?: string;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  className?: string;
  ariaLabel?: string;
};

export function Button({
  children,
  href,
  onClick,
  type = "button",
  variant = "primary",
  disabled,
  className = "",
  ariaLabel,
}: Props) {
  const styles = {
    primary: "bg-forest text-white hover:bg-forest-dark",
    secondary: "border border-forest text-forest bg-white hover:bg-emerald-50",
    ghost: "text-forest hover:bg-emerald-50",
  }[variant];

  const cls = `inline-flex min-h-12 w-full items-center justify-center rounded-xl px-4 text-[15px] font-medium transition ${styles} disabled:opacity-50 ${className}`;

  if (href && !disabled) {
    return (
      <Link href={href} className={cls} aria-label={ariaLabel}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} onClick={onClick} disabled={disabled} className={cls} aria-label={ariaLabel}>
      {children}
    </button>
  );
}
