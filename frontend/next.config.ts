import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  ...(process.env.VERCEL ? {} : { output: "standalone" as const }),
  outputFileTracingRoot: path.join(__dirname),
  transpilePackages: ["maplibre-gl"],
};

export default nextConfig;
