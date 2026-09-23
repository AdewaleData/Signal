import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

const steps = [
  ["Reports", "People nearby say what they see."],
  ["Normalize", "Each report gets a type, place, and time."],
  ["Check", "Matching reports raise confidence. Conflicts stay visible."],
  ["Decide", "Clear, Caution, Avoid, or Not enough information."],
  ["Explain", "You can always see why."],
];

export default function HowItWorksPage() {
  return (
    <main className="mx-auto min-h-dvh max-w-[560px] bg-paper px-5 py-8">
      <Logo />
      <h1 className="mt-8 text-2xl font-semibold tracking-tight">How it works</h1>
      <p className="mt-3 text-[15px] leading-6 text-muted">
        Not a feed. Local reports become a route status.
      </p>
      <ol className="mt-8 space-y-4">
        {steps.map(([title, body], index) => (
          <li key={title} className="rounded-2xl border border-line bg-white p-4">
            <p className="text-xs font-medium text-muted">{index + 1}</p>
            <p className="mt-1 font-medium text-ink">{title}</p>
            <p className="mt-1 text-sm leading-6 text-muted">{body}</p>
          </li>
        ))}
      </ol>
      <p className="mt-8 text-sm leading-6 text-muted">
        Not a safety guarantee. Not emergency services.
      </p>
      <Link href="/home" className="mt-6 flex min-h-12 items-center justify-center rounded-xl bg-forest text-white">
        Continue
      </Link>
    </main>
  );
}
