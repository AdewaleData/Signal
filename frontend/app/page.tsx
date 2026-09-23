import Link from "next/link";
import { Logo } from "@/components/brand/Logo";

export default function SplashPage() {
  return (
    <main className="relative min-h-dvh overflow-hidden text-paper">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/landing.jpg"
        alt=""
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-b from-black/35 via-black/45 to-black/70" />
      <div className="relative mx-auto flex min-h-dvh max-w-[430px] flex-col justify-between px-6 pb-10 pt-16 lg:max-w-[560px]">
        <div className="flex justify-center">
          <Logo light size={72} withWord={false} />
        </div>
        <div className="text-center">
          <h1 className="text-4xl font-semibold tracking-tight">Signal</h1>
          <p className="mt-4 text-lg text-white">Know what&apos;s happening now.</p>
          <p className="mt-2 text-[15px] text-white/80">Make safer decisions.</p>
        </div>
        <div className="space-y-3">
          <Link
            href="/home"
            className="flex min-h-12 items-center justify-center rounded-xl bg-forest text-[15px] font-medium text-white"
          >
            Get started
          </Link>
          <Link href="/how-it-works" className="flex min-h-12 items-center justify-center text-[15px] text-white">
            How it works
          </Link>
        </div>
      </div>
    </main>
  );
}
